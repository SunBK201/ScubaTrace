from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from tree_sitter import Node

from .parser import cpp_parser, java_parser, javascript_parser, python_parser

if TYPE_CHECKING:
    from .file import File
    from .statement import Statement


class Identifier:
    def __init__(self, node: Node, statement: Statement):
        self.node = node
        self.statement = statement

    def __str__(self) -> str:
        return f"{self.signature}: {self.text}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Identifier) and self.signature == value.signature

    def __hash__(self):
        return hash(self.signature)

    @property
    def signature(self) -> str:
        return (
            self.file.signature
            + "line"
            + str(self.start_line)
            + "-"
            + str(self.end_line)
            + "col"
            + str(self.start_column)
            + "-"
            + str(self.end_column)
        )

    @property
    def text(self) -> str:
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def dot_text(self) -> str:
        """
        escape the text ':' for dot
        """
        return '"' + self.text.replace('"', '\\"') + '"'

    @property
    def start_line(self) -> int:
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        return self.node.end_point[0] + 1

    @property
    def start_column(self) -> int:
        return self.node.start_point[1] + 1

    @property
    def end_column(self) -> int:
        return self.node.end_point[1] + 1

    @property
    def length(self):
        return self.end_line - self.start_line + 1

    @property
    def file(self) -> File:
        return self.statement.file

    @property
    def function(self):
        if self.statement.function is None:
            return None
        if "Function" not in self.statement.function.__class__.__name__:
            return None
        return self.statement.function

    @property
    def references(self) -> list[Identifier]:
        func = self.function
        assert func is not None
        identifiers = []
        for identifier in func.identifiers:
            if identifier == self:
                continue
            if identifier.text == self.text:
                identifiers.append(identifier)
        return identifiers

    @property
    @abstractmethod
    def is_left_value(self) -> bool: ...

    @property
    @abstractmethod
    def is_right_value(self) -> bool: ...


class CIdentifier(Identifier):
    @property
    def is_left_value(self) -> bool:
        stat = self.statement
        query = f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (init_declarator
                declarator: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (parameter_declaration
                declarator: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (parameter_declaration
                declarator: (pointer_declarator
                    (identifier)@id
                )
                (#eq? @left "{self.text}")
            )
        """
        nodes = cpp_parser.query_all(stat.node, query)
        for node in nodes:
            if node.start_point == self.node.start_point:
                return True
        return False

    @property
    def is_right_value(self) -> bool:
        return not self.is_left_value


class JavaIdentifier(Identifier):
    @property
    def is_left_value(self) -> bool:
        stat = self.statement
        query = f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (local_variable_declaration
                declarator: (variable_declarator)@left
                (#eq? @left "{self.text}")
            )
            (local_variable_declaration
                declarator: (variable_declarator
                    name: (identifier)@left
                )
                (#eq? @left "{self.text}")
            )
        """
        nodes = java_parser.query_all(stat.node, query)
        for node in nodes:
            if node.start_point == self.node.start_point:
                return True
        return False

    @property
    def is_right_value(self) -> bool:
        return not self.is_left_value


class PythonIdentifier(Identifier):
    @property
    def is_left_value(self) -> bool:
        stat = self.statement
        query = f"""
            (assignment
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (for_statement
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (augmented_assignment
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
        """
        nodes = python_parser.query_all(stat.node, query)
        for node in nodes:
            if node.start_point == self.node.start_point:
                return True
        return False

    @property
    def is_right_value(self) -> bool:
        return not self.is_left_value


class JavaScriptIdentifier(Identifier):
    @property
    def is_left_value(self) -> bool:
        stat = self.statement
        query = f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{self.text}")
            )
            (variable_declarator
                name: (identifier)@left
                (#eq? @left "{self.text}")
            )
        """
        nodes = javascript_parser.query_all(stat.node, query)
        for node in nodes:
            if node.start_point == self.node.start_point:
                return True
        return False

    @property
    def is_right_value(self) -> bool:
        return not self.is_left_value
