# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
import usdex.core
from pxr import Usd

from .data import ConversionData, Tokens
from .urdf_parser.elements import (
    ElementRobot,
    ElementTransmission,
)
from .utils import set_schema_attribute

__all__ = ["convert_transmissions"]


# Transmission data is stored as a custom schema "UrdfPhysicsTransmissionAPI".
def convert_transmissions(data: ConversionData):
    root_element: ElementRobot = data.urdf_parser.get_root_element()
    transmissions: list[ElementTransmission] = root_element.transmissions
    if not len(transmissions):
        return

    geo_scope = data.content[Tokens.Physics].GetDefaultPrim().GetChild(Tokens.Physics).GetPrim()

    for transmission in transmissions:
        name = transmission.get_with_default("name")
        safe_name = data.name_cache.getPrimName(geo_scope, name)

        # create a new prim for the transmission
        transmission_scope = usdex.core.defineScope(geo_scope, safe_name)
        transmission_prim = transmission_scope.GetPrim()
        transmission_prim.ApplyAPI(Usd.SchemaRegistry.GetAPISchemaTypeName("UrdfPhysicsTransmissionAPI"))
        if name != safe_name:
            usdex.core.setDisplayName(transmission_prim, name)

        set_schema_attribute(transmission_prim, "urdf:transmission:name", name)
        if transmission.type and transmission.type.text:
            set_schema_attribute(transmission_prim, "urdf:transmission:type", transmission.type.text)
        if transmission.joint and transmission.joint.name:
            set_schema_attribute(transmission_prim, "urdf:transmission:joint:name", transmission.joint.name)
        if transmission.joint and transmission.joint.hardwareInterface and transmission.joint.hardwareInterface.text:
            set_schema_attribute(transmission_prim, "urdf:transmission:joint:hardwareInterface", transmission.joint.hardwareInterface.text)
        if transmission.actuator and transmission.actuator.name:
            set_schema_attribute(transmission_prim, "urdf:transmission:actuator:name", transmission.actuator.name)
        if transmission.actuator and transmission.actuator.mechanicalReduction and transmission.actuator.mechanicalReduction.text:
            set_schema_attribute(
                transmission_prim, "urdf:transmission:actuator:mechanicalReduction", float(transmission.actuator.mechanicalReduction.text)
            )
        if transmission.actuator and transmission.actuator.hardwareInterface and transmission.actuator.hardwareInterface.text:
            set_schema_attribute(transmission_prim, "urdf:transmission:actuator:hardwareInterface", transmission.actuator.hardwareInterface.text)
