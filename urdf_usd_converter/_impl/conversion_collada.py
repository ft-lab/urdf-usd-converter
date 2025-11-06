# SPDX-FileCopyrightText: Copyright (c) 2025 The Newton Developers
# SPDX-License-Identifier: Apache-2.0
import pathlib

import collada
import usdex.core
from pxr import Tf, Usd, UsdGeom, Vt

from .data import ConversionData
from .numpy import convert_face_indices_array, convert_matrix4d, convert_vec2f_array, convert_vec3f_array

__all__ = ["ConversionCollada"]


class ConversionCollada:
    def __init__(self, input_path: pathlib.Path):
        try:
            self.collada = collada.Collada(str(input_path))
        except Exception as e:
            Tf.RaiseRuntimeError(f'Invalid input_path: "{input_path!s}" could not be parsed. {e}')

        # The default unit for the scene is meters (= 1.0).
        self.unit_meter = self.collada.assetInfo.unitmeter if self.collada.assetInfo.unitmeter is not None else 1.0

    def _convert_mesh(self, parent_prim: Usd.Prim, geometry: collada.geometry.Geometry, data: ConversionData):
        name = geometry.name
        safe_name = data.name_cache.getPrimName(parent_prim, name)
        for primitive in geometry.primitives:
            primitive_type = type(primitive).__name__
            if primitive_type in ["TriangleSet", "Triangles", "Polylist", "Polygons"]:
                vertices = None
                normals = None
                uvs = None
                face_vertex_indices = None
                face_vertex_counts = None

                # vertex indices.
                if primitive_type == "TriangleSet":
                    face_vertex_counts, face_vertex_indices = convert_face_indices_array(primitive.vertex_index)
                elif primitive_type == "Polylist" or primitive_type == "Polygons":
                    face_vertex_counts = [int(i) for i in primitive.vcounts]
                    face_vertex_indices = [int(i) for i in primitive.vertex_index]
                elif primitive_type == "Triangles":
                    face_vertex_counts = [3] * len(primitive.vertex_index)
                    face_vertex_indices = [int(i) for i in primitive.vertex_index]

                if hasattr(primitive, "vertex"):
                    vertices = convert_vec3f_array(primitive.vertex)

                if hasattr(primitive, "normal"):
                    primitive_normals = convert_vec3f_array(primitive.normal)
                    normal_indices = primitive.normal_index

                    if primitive_type == "TriangleSet" or primitive_type == "Triangles":
                        normal_indices = [int(j) for sublist in normal_indices for j in sublist]
                    elif primitive_type == "Polylist" or primitive_type == "Polygons":
                        normal_indices = [int(j) for j in normal_indices]
                    normals = usdex.core.Vec3fPrimvarData(UsdGeom.Tokens.faceVarying, primitive_normals, Vt.IntArray(normal_indices))
                    normals.index()  # re-index the normals to remove duplicates

                # UVs.
                # If there are multiple UV layers, the first UV layer is used.
                if hasattr(primitive, "texcoordset") and len(primitive.texcoordset) > 0:
                    uv_data = convert_vec2f_array(primitive.texcoordset[0])
                    if len(uv_data) == len(face_vertex_indices):
                        uv_indices = list(range(len(uv_data)))
                        uvs = usdex.core.Vec2fPrimvarData(UsdGeom.Tokens.faceVarying, uv_data, Vt.IntArray(uv_indices))
                        uvs.index()  # re-index the uvs to remove duplicates

                if face_vertex_counts is not None and face_vertex_indices is not None and vertices is not None:
                    usd_mesh = usdex.core.definePolyMesh(
                        parent_prim,
                        safe_name,
                        faceVertexCounts=Vt.IntArray(face_vertex_counts),
                        faceVertexIndices=Vt.IntArray(face_vertex_indices),
                        points=Vt.Vec3fArray(vertices),
                        normals=normals,
                        uvs=uvs,
                    )
                    if not usd_mesh:
                        Tf.RaiseRuntimeError(f'Failed to convert mesh "{parent_prim.GetPath()}"')

                    if name != safe_name:
                        usdex.core.setDisplayName(usd_mesh.GetPrim(), name)

    def convert(self, parent_prim: Usd.Prim, data: ConversionData):
        """
        Trace the hierarchical structure and place the geometry.
        """
        for scene in self.collada.scenes:
            for node in scene.nodes:
                self._convert_nest(node, parent_prim, data)

        return parent_prim

    def _convert_nest(self, node: collada.scene.Node, parent_prim: Usd.Prim, data: ConversionData, depth: int = 0) -> Usd.Prim:
        node_name = node.name if hasattr(node, "name") else None

        target_prim = parent_prim
        if isinstance(node, collada.scene.Node) and node_name is not None:
            safe_name = data.name_cache.getPrimName(parent_prim, node_name)
            xform = usdex.core.defineXform(parent_prim, safe_name)
            if node_name != safe_name:
                usdex.core.setDisplayName(xform.GetPrim(), node_name)

            # Set the transformation matrix if available
            node_matrix = node.matrix if hasattr(node, "matrix") else None
            if node_matrix is not None:
                usd_matrix = convert_matrix4d(node_matrix)

                # Metric scaling.
                if depth == 0:
                    usd_matrix = usd_matrix * (1.0 / self.unit_meter)

                usdex.core.setLocalTransform(xform, usd_matrix)

            target_prim = xform.GetPrim()

        # Geometry Node.
        if isinstance(node, collada.scene.GeometryNode):
            self._convert_mesh(target_prim, node.geometry, data)

        if hasattr(node, "children") and node.children:
            for child in node.children:
                self._convert_nest(child, target_prim, data, depth + 1)

        return target_prim
