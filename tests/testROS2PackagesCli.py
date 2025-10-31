# SPDX-FileCopyrightText: Copyright (c) 2025 The Newton Developers
# SPDX-License-Identifier: Apache-2.0
import pathlib
import shutil
from unittest.mock import patch

from tests.util.ConverterTestCase import ConverterTestCase
from urdf_usd_converter._impl.cli import run


class TestROS2PackagesCli(ConverterTestCase):
    def test_do_not_specify_ros2_package_name(self):
        # If the `package` argument is not specified in `converter.convert`.
        # In this case, if the mesh or texture URI specifies "package://PackageName/foo/test.png",
        # this will be removed and treated as a relative path "foo/test.png".
        input_path = "tests/data/simple_ref_ros2_package.urdf"
        output_dir = self.tmpDir()

        with patch("sys.argv", ["urdf_usd_converter", input_path, output_dir]):
            self.assertEqual(run(), 0, f"Failed to convert {input_path}")

        # TODO: Here we need to make sure that the reference to the usd file is correct after the mesh or texture is loaded.

    def test_specify_ros2_package_names(self):
        """
        Specify ROS2 package arguments as CLI
        """
        input_path = "tests/data/simple_ref_ros2_package.urdf"
        output_dir = self.tmpDir()

        test_package_dir = output_dir + "/temp"
        test_texture_package_dir = output_dir + "/temp/textures"
        pathlib.Path(test_package_dir + "/assets").mkdir(parents=True, exist_ok=True)
        pathlib.Path(test_texture_package_dir + "/assets").mkdir(parents=True, exist_ok=True)

        # Copy "tests/data/assets/box.stl" to test_package_dir
        shutil.copy("tests/data/assets/box.stl", test_package_dir + "/assets")

        # Copy "tests/data/assets/grid.png" to test_texture_package_dir
        shutil.copy("tests/data/assets/grid.png", test_texture_package_dir + "/assets")

        temp_stl_file_path = test_package_dir + "/assets/box.stl"
        temp_texture_file_path = test_texture_package_dir + "/assets/grid.png"
        self.assertTrue(pathlib.Path(temp_stl_file_path).exists())
        self.assertTrue(pathlib.Path(temp_texture_file_path).exists())

        with patch(
            "sys.argv",
            [
                "urdf_usd_converter",
                input_path,
                output_dir,
                "--package",
                "test_package=" + test_package_dir,
                "--package",
                "test_texture_package=" + test_texture_package_dir,
            ],
        ):
            self.assertEqual(run(), 0, f"Failed to convert {input_path}")

        # TODO: Here we need to make sure that the reference to the usd file is correct after the mesh or texture is loaded.
