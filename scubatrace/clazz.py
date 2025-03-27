from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from tree_sitter import Node

from . import language
from .method import CPPMethod, JavaMethod, JavaScriptMethod, PythonMethod
from .parser import cpp_parser, java_parser, javascript_parser, python_parser

if TYPE_CHECKING:
    from .file import File
    from .method import Method


class Class:
    def __init__(self, node: Node, file: File) -> None:
        self.node = node
        self.file = file

    def __str__(self) -> str:
        return self.signature

    @property
    def signature(self) -> str:
        return (
            self.file.signature
            + "#"
            + self.name
            + "#"
            + str(self.start_line)
            + "#"
            + str(self.end_line)
        )

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
    def name(self) -> str:
        class_name = self.node.child_by_field_name("name")
        assert class_name is not None
        assert class_name.text is not None
        return class_name.text.decode()

    @property
    @abstractmethod
    def methods(self) -> list[Method]: ...

    @property
    @abstractmethod
    def fields(self) -> list[str]: ...


class CPPClass(Class):
    @property
    def methods(self) -> list[Method]:
        method_nodes = cpp_parser.query_all(self.node, language.CPP.query_method)
        return [CPPMethod(node, self) for node in method_nodes]

    @property
    def fields(self) -> list[str]:
        field_nodes = cpp_parser.query_all(self.node, language.CPP.query_field)
        return [node.text.decode() for node in field_nodes]  # type: ignore


class JavaClass(Class):
    @property
    def methods(self) -> list[Method]:
        method_nodes = java_parser.query_all(self.node, language.JAVA.query_method)
        return [JavaMethod(node, self) for node in method_nodes]


class PythonClass(Class):
    @property
    def methods(self) -> list[Method]:
        method_nodes = python_parser.query_all(
            self.node, language.PYTHON.query_function
        )
        return [PythonMethod(node, self) for node in method_nodes]


class JavaScriptClass(Class):
    @property
    def methods(self) -> list[Method]:
        method_nodes = javascript_parser.query_all(
            self.node, language.JAVASCRIPT.query_method
        )
        return [JavaScriptMethod(node, self) for node in method_nodes]
