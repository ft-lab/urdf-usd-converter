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
        self.assertFalse(warning_obj_found, "Expected warning about obj format not found.")
        self.assertTrue(warning_dae_found, "Expected warning about dae format not found.")
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

    def test_obj_single_mesh(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertIsNotNone(default_prim)

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertIsNotNone(geom_scope_prim)

        link_prim_path = geom_scope_prim.GetPath().AppendChild("link_mesh_stl").AppendChild("link_mesh_obj")
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertIsNotNone(link_prim)
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        box_prim_path = link_prim_path.AppendChild("box")
        box_prim = self.stage.GetPrimAtPath(box_prim_path)
        self.assertIsNotNone(box_prim)
        self.assertTrue(box_prim.IsA(UsdGeom.Xform))

        # A Mesh prim exists as a child of the Xform prim in the link.
        mesh_prim = box_prim.GetChild("box_1")
        self.assertIsNotNone(mesh_prim)
        self.assertTrue(mesh_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(mesh_prim.GetReferences())

        usd_mesh_stl = UsdGeom.Mesh(mesh_prim)
        self.assertTrue(usd_mesh_stl.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_stl.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_stl.GetFaceVertexIndicesAttr().HasAuthoredValue())

    def test_obj_two_meshes(self):
        default_prim = self.stage.GetDefaultPrim()
        self.assertIsNotNone(default_prim)

        geom_scope_prim = self.stage.GetPrimAtPath(default_prim.GetPath().AppendChild("Geometry"))
        self.assertIsNotNone(geom_scope_prim)

        link_prim_path = geom_scope_prim.GetPath().AppendChild("link_mesh_stl").AppendChild("link_mesh_multi_objs")
        link_prim = self.stage.GetPrimAtPath(link_prim_path)
        self.assertIsNotNone(link_prim)
        self.assertTrue(link_prim.IsA(UsdGeom.Xform))

        # When an obj file contains multiple meshes, each mesh exists as a child of the Xform.
        two_boxes_prim_path = link_prim_path.AppendChild("two_boxes")

        two_boxes_prim = self.stage.GetPrimAtPath(two_boxes_prim_path)
        self.assertIsNotNone(two_boxes_prim)
        self.assertTrue(two_boxes_prim.IsA(UsdGeom.Xform))
        self.assertEqual(UsdGeom.Imageable(two_boxes_prim).GetPurposeAttr().Get(), UsdGeom.Tokens.default_)

        cube_red_prim = two_boxes_prim.GetChild("Cube_Red")
        self.assertIsNotNone(cube_red_prim)
        self.assertTrue(cube_red_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(cube_red_prim.GetReferences())

        usd_mesh_red = UsdGeom.Mesh(cube_red_prim)
        self.assertTrue(usd_mesh_red.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_red.GetFaceVertexIndicesAttr().HasAuthoredValue())

        cube_green_prim = two_boxes_prim.GetChild("Cube_Green")
        self.assertIsNotNone(cube_green_prim)
        self.assertTrue(cube_green_prim.IsA(UsdGeom.Mesh))
        self.assertTrue(cube_green_prim.GetReferences())

        usd_mesh_green = UsdGeom.Mesh(cube_green_prim)
        self.assertTrue(usd_mesh_green.GetPointsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexCountsAttr().HasAuthoredValue())
        self.assertTrue(usd_mesh_green.GetFaceVertexIndicesAttr().HasAuthoredValue())

        two_boxes_collision_prim_path = link_prim_path.AppendChild("two_boxes_1")
        two_boxes_collision_prim = self.stage.GetPrimAtPath(two_boxes_collision_prim_path)
        self.assertIsNotNone(two_boxes_collision_prim)
        self.assertTrue(two_boxes_collision_prim.IsA(UsdGeom.Xform))
        self.assertEqual(UsdGeom.Imageable(two_boxes_collision_prim).GetPurposeAttr().Get(), UsdGeom.Tokens.guide)
