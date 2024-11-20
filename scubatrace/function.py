from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from tree_sitter import Node

from . import language
from .parser import c_parser
from .statement import Statement

if TYPE_CHECKING:
    from .file import File


class Function:
    def __init__(self, node: Node, file: File):
        self.node = node
        self.file = file

    def __str__(self) -> str:
        return f"{self.name}({self.start_line}-{self.end_line})"

    @property
    def text(self) -> str:
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def start_line(self) -> int:
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        return self.node.end_point[0] + 1

    @property
    def length(self):
        return self.end_line - self.start_line + 1

    @property
    def lines(self) -> dict[int, str]:
        return {
            i + self.start_line: line for i, line in enumerate(self.text.split("\n"))
        }

    @property
    def body_node(self) -> Node | None:
        return self.node.child_by_field_name("body")

    @property
    def body_start_line(self) -> int:
        if self.body_node is None:
            return self.start_line
        else:
            return self.body_node.start_point[0] + 1

    @property
    def body_end_line(self) -> int:
        if self.body_node is None:
            return self.end_line
        else:
            return self.body_node.end_point[0] + 1

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def identifiers(self) -> dict[Node, str]: ...

    @property
    @abstractmethod
    def variables(self) -> dict[Node, str]: ...

    @property
    @abstractmethod
    def accessible_functions(self) -> list[Function]: ...

    @property
    @abstractmethod
    def calls(self) -> list[Statement]: ...

    @property
    @abstractmethod
    def callees(self) -> dict[Function, list[Statement]]: ...

    @property
    @abstractmethod
    def callers(self) -> dict[Function, list[Statement]]: ...


class CFunction(Function):
    def __init__(self, node: Node, file):
        super().__init__(node, file)

    @property
    def name(self) -> str:
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
        assert name_node.text is not None
        return name_node.text.decode()

    @property
    def identifiers(self) -> dict[Node, str]:
        nodes = c_parser.query_all(self.node, language.C.query_identifier)
        identifiers = {
            node: node.text.decode() for node in nodes if node.text is not None
        }
        return identifiers

    @property
    def variables(self) -> dict[Node, str]:
        variables = self.identifiers
        for node in self.identifiers:
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
            ]:
                variables.pop(node)
        return variables

    @property
    def calls(self) -> list[Statement]:
        # nodes = c_parser.query_all(self.node, language.C.query_call)
        # calls = {node: node.text.decode() for node in nodes if node.text is not None}
        ...

    @property
    def accessible_functions(self) -> list[Function]:
        funcs = []
        for file in self.file.imports:
            for function in file.functions:
                funcs.append(function)
        return funcs
