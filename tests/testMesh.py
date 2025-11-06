# SPDX-FileCopyrightText: Copyright (c) 2025 The Newton Developers
# SPDX-License-Identifier: Apache-2.0
import pathlib

import usdex.core
import usdex.test
from pxr import Tf, Usd, UsdGeom

import urdf_usd_converter
from tests.util.ConverterTestCase import ConverterTestCase


class TestMesh(ConverterTestCase):
    def setUp(self):
        super().setUp()

        input_path = "tests/data/meshes.urdf"
        output_dir = self.tmpDir()

        converter = urdf_usd_converter.Converter()
        with usdex.test.ScopedDiagnosticChecker(
            self,
            [
                (Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*The obj format is not yet supported:.*"),
                (Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*Unsupported mesh format:.*"),
            ],
            level=usdex.core.DiagnosticsLevel.eWarning,
        ):
            asset_path = converter.convert(input_path, output_dir)

        self.assertIsNotNone(asset_path)
        self.assertTrue(pathlib.Path(asset_path.path).exists())

        self.stage: Usd.Stage = Usd.Stage.Open(asset_path.path)
        self.assertIsValidUsd(self.stage)

    def test_stl_mesh(self):
        default_prim = self.stage.GetDefaultPrim()
        geometry_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertTrue(geometry_scope_prim.IsValid())

        # Test STL mesh conversion
        link_stl_prim = self.stage.GetPrimAtPath(geometry_scope_prim.GetPath().AppendChild("link_mesh_stl"))
        self.assertTrue(link_stl_prim.IsValid())
        self.assertTrue(link_stl_prim.IsA(UsdGeom.Xform))

        stl_mesh_prim = self.stage.GetPrimAtPath(link_stl_prim.GetPath().AppendChild("box"))
        self.assertTrue(stl_mesh_prim.IsValid())
        self.assertTrue(stl_mesh_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(stl_mesh_prim.HasAuthoredReferences())

        usd_mesh_stl = UsdGeom.Mesh(stl_mesh_prim)
        self.assertTrue(usd_mesh_stl.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_stl.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_stl.GetFaceVertexIndicesAttr().HasAuthoredValue())
        # The sample box.stl has normals and they are authored as a primvar
        self.assertFalse(usd_mesh_stl.GetNormalsAttr().HasAuthoredValue())
        normals_primvar: UsdGeom.Primvar = UsdGeom.PrimvarsAPI(usd_mesh_stl).GetPrimvar("normals")
        self.assertTrue(normals_primvar.IsDefined())
        self.assertTrue(normals_primvar.HasAuthoredValue())
        self.assertTrue(normals_primvar.GetIndicesAttr().HasAuthoredValue())
        self.assertEqual(UsdGeom.Imageable(stl_mesh_prim).GetPurposeAttr().Get(), UsdGeom.Tokens.default_)

    def test_dae_single_mesh(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertTrue(default_prim.IsValid())

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertTrue(geom_scope_prim.IsValid())

        link_prim_path = geom_scope_prim.GetPath().AppendChild("link_mesh_stl").AppendChild("link_mesh_obj").AppendChild("link_mesh_dae")
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertTrue(link_prim.IsValid())
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("box")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertTrue(box_prim.IsValid())
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.HasAuthoredReferences())

        cube_prim_path = box_prim_path.AppendChild("Cube")
        cube_prim = self.stage.GetPrimAtPath(cube_prim_path)
        self.assertTrue(cube_prim.IsValid())
        self.assertTrue(cube_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_prim = cube_prim.GetChild("Cube")
        self.assertTrue(mesh_prim.IsValid())
        self.assertTrue(mesh_prim.IsA(UsdGeom.Mesh))

        usd_mesh_obj = UsdGeom.Mesh(mesh_prim)
        self.assertTrue(usd_mesh_obj.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_obj.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_obj.GetFaceVertexIndicesAttr().HasAuthoredValue())

        box_collision_prim_path = link_prim_path.AppendChild("box_1")
        box_collision_prim = self.stage.GetPrimAtPath(box_collision_prim_path)
        self.assertTrue(box_collision_prim.IsValid())
        self.assertTrue(box_collision_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_collision_prim.HasAuthoredReferences())

        cube_collision_prim_path = box_collision_prim_path.AppendChild("Cube")
        cube_collision_prim = self.stage.GetPrimAtPath(cube_collision_prim_path)
        self.assertTrue(cube_collision_prim.IsValid())
        self.assertTrue(cube_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_collision_prim = cube_collision_prim.GetChild("Cube")
        self.assertTrue(mesh_collision_prim.IsValid())
        self.assertTrue(mesh_collision_prim.IsA(UsdGeom.Mesh))

        usd_mesh_collision = UsdGeom.Mesh(mesh_collision_prim)
        self.assertTrue(usd_mesh_collision.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_collision.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_collision.GetFaceVertexIndicesAttr().HasAuthoredValue())

    def test_dae_two_meshes(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertTrue(default_prim.IsValid())

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertTrue(geom_scope_prim.IsValid())

        link_prim_path = (
            geom_scope_prim.GetPath()
            .AppendChild("link_mesh_stl")
            .AppendChild("link_mesh_obj")
            .AppendChild("link_mesh_dae")
            .AppendChild("link_two_meshes_dae")
        )
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertTrue(link_prim.IsValid())
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("two_meshes")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertTrue(box_prim.IsValid())
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.HasAuthoredReferences())

        cubes_prim_path = box_prim_path.AppendChild("cubes")
        cubes_prim = self.stage.GetPrimAtPath(cubes_prim_path)
        self.assertTrue(cubes_prim.IsValid())
        self.assertTrue(cubes_prim.IsA(UsdGeom.Xform))

        cube_red_prim_path = cubes_prim_path.AppendChild("Cube_Red")
        cube_red_prim = self.stage.GetPrimAtPath(cube_red_prim_path)
        self.assertTrue(cube_red_prim.IsValid())
        self.assertTrue(cube_red_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_red_prim = cube_red_prim.GetChild("Cube")
        self.assertTrue(mesh_red_prim.IsValid())
        self.assertTrue(mesh_red_prim.IsA(UsdGeom.Mesh))

        usd_mesh_red = UsdGeom.Mesh(mesh_red_prim)
        self.assertTrue(usd_mesh_red.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexIndicesAttr().HasAuthoredValue())

        cube_green_prim_path = cubes_prim_path.AppendChild("Cube_Green")
        cube_green_prim = self.stage.GetPrimAtPath(cube_green_prim_path)
        self.assertTrue(cube_green_prim.IsValid())
        self.assertTrue(cube_green_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_green_prim = cube_green_prim.GetChild("tn__Cube001_VB")
        self.assertTrue(mesh_green_prim.IsValid())
        self.assertTrue(mesh_green_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(usdex.core.getDisplayName(mesh_green_prim), "Cube.001")

        usd_mesh_green = UsdGeom.Mesh(mesh_green_prim)
        self.assertTrue(usd_mesh_green.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexIndicesAttr().HasAuthoredValue())

    def test_dae_two_triangle_meshes(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertTrue(default_prim.IsValid())

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertTrue(geom_scope_prim.IsValid())

        link_prim_path = (
            geom_scope_prim.GetPath()
            .AppendChild("link_mesh_stl")
            .AppendChild("link_mesh_obj")
            .AppendChild("link_mesh_dae")
            .AppendChild("link_two_meshes_dae")
            .AppendChild("link_two_meshes_triangle_dae")
        )
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertTrue(link_prim.IsValid())
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("two_meshes_triangle")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertTrue(box_prim.IsValid())
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.HasAuthoredReferences())

        cubes_prim_path = box_prim_path.AppendChild("cubes")
        cubes_prim = self.stage.GetPrimAtPath(cubes_prim_path)
        self.assertTrue(cubes_prim.IsValid())
        self.assertTrue(cubes_prim.IsA(UsdGeom.Xform))

        cube_red_prim_path = cubes_prim_path.AppendChild("Cube_Red")
        cube_red_prim = self.stage.GetPrimAtPath(cube_red_prim_path)
        self.assertTrue(cube_red_prim.IsValid())
        self.assertTrue(cube_red_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_red_prim = cube_red_prim.GetChild("Cube")
        self.assertTrue(mesh_red_prim.IsValid())
        self.assertTrue(mesh_red_prim.IsA(UsdGeom.Mesh))

        usd_mesh_red = UsdGeom.Mesh(mesh_red_prim)
        self.assertTrue(usd_mesh_red.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexIndicesAttr().HasAuthoredValue())

        cube_green_prim_path = cubes_prim_path.AppendChild("Cube_Green")
        cube_green_prim = self.stage.GetPrimAtPath(cube_green_prim_path)
        self.assertTrue(cube_green_prim.IsValid())
        self.assertTrue(cube_green_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_green_prim = cube_green_prim.GetChild("tn__Cube001_VB")
        self.assertTrue(mesh_green_prim.IsValid())
        self.assertTrue(mesh_green_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(usdex.core.getDisplayName(mesh_green_prim), "Cube.001")

        usd_mesh_green = UsdGeom.Mesh(mesh_green_prim)
        self.assertTrue(usd_mesh_green.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexIndicesAttr().HasAuthoredValue())
