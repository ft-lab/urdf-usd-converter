# SPDX-FileCopyrightText: Copyright (c) 2025 The Newton Developers
# SPDX-License-Identifier: Apache-2.0
import pathlib
from unittest.mock import patch

from pxr import Usd, UsdGeom

from tests.util.ConverterTestCase import ConverterTestCase
from urdf_usd_converter._impl.convert import Converter


class TestConverterLoadMeshes(ConverterTestCase):
    @patch("urdf_usd_converter._impl.mesh.Tf.Warn")
    def test_mesh_conversion(self, mock_warn):
        input_path = "tests/data/simple_meshes.urdf"
        output_dir = self.tmpDir()

        converter = Converter()
        asset_path = converter.convert(input_path, output_dir)
        self.assertIsNotNone(asset_path)
        self.assertTrue(pathlib.Path(asset_path.path).exists())

        # Verify that Tf.Warn was called with the expected message
        mock_warn.assert_called()

        # Check if any call contains the mesh format warning
        warning_stl_found = False
        warning_obj_found = False
        warning_dae_found = False
        warning_dxf_found = False
        for call in mock_warn.call_args_list:
            if "The stl format is not yet supported:" in str(call):
                warning_stl_found = True
            if "The obj format is not yet supported:" in str(call):
                warning_obj_found = True
            if "The dae format is not yet supported:" in str(call):
                warning_dae_found = True
            if "Unsupported mesh format:" in str(call):
                warning_dxf_found = True

        self.assertTrue(warning_stl_found, "Expected warning about stl format not found.")
        self.assertTrue(warning_obj_found, "Expected warning about obj format not found.")
        self.assertFalse(warning_dae_found, "Expected warning about dae format not found.")
        self.assertTrue(warning_dxf_found, "Expected warning about dxf format not found.")


class TestConverterMeshes(ConverterTestCase):
    def setUp(self):
        super().setUp()

        input_path = "tests/data/simple_meshes.urdf"
        output_dir = self.tmpDir()

        converter = Converter()
        asset_path = converter.convert(input_path, output_dir)
        self.assertIsNotNone(asset_path)
        self.assertTrue(pathlib.Path(asset_path.path).exists())

        self.stage: Usd.Stage = Usd.Stage.Open(asset_path.path)
        self.assertIsValidUsd(self.stage)

    def test_dae_single_mesh(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertIsNotNone(default_prim)

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertIsNotNone(geom_scope_prim)

        link_prim_path = geom_scope_prim.GetPath().AppendChild("link_mesh_stl").AppendChild("link_mesh_obj").AppendChild("link_mesh_dae")
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertIsNotNone(link_prim)
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("box")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertIsNotNone(box_prim)
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.GetReferences())

        cube_prim_path = box_prim_path.AppendChild("Cube")
        cube_prim = self.stage.GetPrimAtPath(cube_prim_path)
        self.assertIsNotNone(cube_prim)
        self.assertTrue(cube_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_prim = cube_prim.GetChild("Cube")
        self.assertIsNotNone(mesh_prim)
        self.assertTrue(mesh_prim.IsA(UsdGeom.Mesh))

        usd_mesh_obj = UsdGeom.Mesh(mesh_prim)
        self.assertTrue(usd_mesh_obj.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_obj.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_obj.GetFaceVertexIndicesAttr().HasAuthoredValue())

        box_collision_prim_path = link_prim_path.AppendChild("box_1")
        box_collision_prim = self.stage.GetPrimAtPath(box_collision_prim_path)
        self.assertIsNotNone(box_collision_prim)
        self.assertTrue(box_collision_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_collision_prim.GetReferences())

        cube_collision_prim_path = box_collision_prim_path.AppendChild("Cube")
        cube_collision_prim = self.stage.GetPrimAtPath(cube_collision_prim_path)
        self.assertIsNotNone(cube_collision_prim)
        self.assertTrue(cube_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_collision_prim = cube_collision_prim.GetChild("Cube")
        self.assertIsNotNone(mesh_collision_prim)
        self.assertTrue(mesh_collision_prim.IsA(UsdGeom.Mesh))

        usd_mesh_collision = UsdGeom.Mesh(mesh_collision_prim)
        self.assertTrue(usd_mesh_collision.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_collision.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_collision.GetFaceVertexIndicesAttr().HasAuthoredValue())

    def test_dae_two_meshes(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertIsNotNone(default_prim)

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertIsNotNone(geom_scope_prim)

        link_prim_path = (
            geom_scope_prim.GetPath()
            .AppendChild("link_mesh_stl")
            .AppendChild("link_mesh_obj")
            .AppendChild("link_mesh_dae")
            .AppendChild("link_two_meshes_dae")
        )
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertIsNotNone(link_prim)
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("two_meshes")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertIsNotNone(box_prim)
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.GetReferences())

        cubes_prim_path = box_prim_path.AppendChild("cubes")
        cubes_prim = self.stage.GetPrimAtPath(cubes_prim_path)
        self.assertIsNotNone(cubes_prim)
        self.assertTrue(cubes_prim.IsA(UsdGeom.Xform))

        cube_red_prim_path = cubes_prim_path.AppendChild("Cube_Red")
        cube_red_prim = self.stage.GetPrimAtPath(cube_red_prim_path)
        self.assertIsNotNone(cube_red_prim)
        self.assertTrue(cube_red_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_red_prim = cube_red_prim.GetChild("Cube")
        self.assertIsNotNone(mesh_red_prim)
        self.assertTrue(mesh_red_prim.IsA(UsdGeom.Mesh))

        usd_mesh_red = UsdGeom.Mesh(mesh_red_prim)
        self.assertTrue(usd_mesh_red.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexIndicesAttr().HasAuthoredValue())

        cube_green_prim_path = cubes_prim_path.AppendChild("Cube_Green")
        cube_green_prim = self.stage.GetPrimAtPath(cube_green_prim_path)
        self.assertIsNotNone(cube_green_prim)
        self.assertTrue(cube_green_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_green_prim = cube_green_prim.GetChild("tn__Cube001_VB")
        self.assertIsNotNone(mesh_green_prim)
        self.assertTrue(mesh_green_prim.IsA(UsdGeom.Mesh))

        usd_mesh_green = UsdGeom.Mesh(mesh_green_prim)
        self.assertTrue(usd_mesh_green.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexIndicesAttr().HasAuthoredValue())

    def test_dae_two_triangle_meshes(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertIsNotNone(default_prim)

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertIsNotNone(geom_scope_prim)

        link_prim_path = (
            geom_scope_prim.GetPath()
            .AppendChild("link_mesh_stl")
            .AppendChild("link_mesh_obj")
            .AppendChild("link_mesh_dae")
            .AppendChild("link_two_meshes_dae")
            .AppendChild("link_two_meshes_triangle_dae")
        )
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertIsNotNone(link_prim)
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("two_meshes_triangle")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertIsNotNone(box_prim)
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))
        self.assertTrue(box_prim.GetReferences())

        cubes_prim_path = box_prim_path.AppendChild("cubes")
        cubes_prim = self.stage.GetPrimAtPath(cubes_prim_path)
        self.assertIsNotNone(cubes_prim)
        self.assertTrue(cubes_prim.IsA(UsdGeom.Xform))

        cube_red_prim_path = cubes_prim_path.AppendChild("Cube_Red")
        cube_red_prim = self.stage.GetPrimAtPath(cube_red_prim_path)
        self.assertIsNotNone(cube_red_prim)
        self.assertTrue(cube_red_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_red_prim = cube_red_prim.GetChild("Cube")
        self.assertIsNotNone(mesh_red_prim)
        self.assertTrue(mesh_red_prim.IsA(UsdGeom.Mesh))

        usd_mesh_red = UsdGeom.Mesh(mesh_red_prim)
        self.assertTrue(usd_mesh_red.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexIndicesAttr().HasAuthoredValue())

        cube_green_prim_path = cubes_prim_path.AppendChild("Cube_Green")
        cube_green_prim = self.stage.GetPrimAtPath(cube_green_prim_path)
        self.assertIsNotNone(cube_green_prim)
        self.assertTrue(cube_green_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_green_prim = cube_green_prim.GetChild("tn__Cube001_VB")
        self.assertIsNotNone(mesh_green_prim)
        self.assertTrue(mesh_green_prim.IsA(UsdGeom.Mesh))

        usd_mesh_green = UsdGeom.Mesh(mesh_green_prim)
        self.assertTrue(usd_mesh_green.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexIndicesAttr().HasAuthoredValue())
