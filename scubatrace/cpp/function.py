from __future__ import annotations

from functools import cached_property

from tree_sitter import Node

from ..function import Function
from .statement import CBlockStatement


class CFunction(Function, CBlockStatement):
    @cached_property
    def name_node(self) -> Node:
        name_node = self.node.child_by_field_name("declarator")
        while name_node is not None and name_node.type not in {
            "identifier",
            "operator_name",
            "type_identifier",
        }:
            all_temp_name_node = name_node
            if (
                name_node.child_by_field_name("declarator") is None
                and name_node.type == "reference_declarator"
            ):
                for temp_node in name_node.children:
                    if temp_node.type == "function_declarator":
                        name_node = temp_node
                        break
            if name_node.child_by_field_name("declarator") is not None:
                name_node = name_node.child_by_field_name("declarator")
            # int *a()
            if (
                name_node is not None
                and name_node.type == "field_identifier"
                and name_node.child_by_field_name("declarator") is None
            ):
                break
            if name_node == all_temp_name_node:
                break
        assert name_node is not None
        return name_node

    @cached_property
    def parameter_lines(self) -> list[int]:
        declarator_node = self.node.child_by_field_name("declarator")
        if declarator_node is None:
            return [self.start_line]
        param_node = declarator_node.child_by_field_name("parameters")
        if param_node is None:
            return [self.start_line]
        param_node_start_line = param_node.start_point[0] + 1
        param_node_end_line = param_node.end_point[0] + 1
        return list(range(param_node_start_line, param_node_end_line + 1))
