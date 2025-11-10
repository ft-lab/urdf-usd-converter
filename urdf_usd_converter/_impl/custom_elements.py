# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import usdex.core
from pxr import Usd

from .data import ConversionData, Tokens
from .urdf_parser.undefined_data import UndefinedData


def convert_custom_elements(data: ConversionData):
    # TODO: Implement custom elements conversion.
    undefined_elements: list[UndefinedData] = data.urdf_parser.get_undefined_elements()

    default_prim = data.content[Tokens.Contents].GetDefaultPrim()
    contents_scope = default_prim.GetChild(Tokens.Contents)
    if not contents_scope:
        contents_scope = usdex.core.defineScope(default_prim, Tokens.Contents)

    for undefined_element in undefined_elements:
        prim: Usd.Prim = contents_scope.GetPrim()

        element_list = [element for element in undefined_element.path.split("/") if element != ""]

        for element in element_list:
            child_prim = prim.GetChild(element)
            if not child_prim:
                prim = usdex.core.defineScope(prim, element).GetPrim()
            else:
                prim = child_prim
