from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from tree_sitter import Node

from . import language as lang
from .function import Function
from .statement import BlockStatement

if TYPE_CHECKING:
    from .file import File


class Class(BlockStatement):
    """
    A class in the source code.
    """

    def __init__(self, node: Node, file: File | BlockStatement) -> None:
        super().__init__(node, file)

    @staticmethod
    def create(node: Node, parent: File | BlockStatement):
        """
        Factory function to create a Class instance based on the language of the file.

        Args:
            node (Node): The tree-sitter node representing the class.
            file (File): The file containing the class.

        Returns:
            Class: An instance of a language-specific Class subclass corresponding to the file's language.
        """
        if parent.project.language == lang.C:
            from .cpp.clazz import CClass

            return CClass(node, parent)
        elif parent.project.language == lang.JAVA:
            from .java.clazz import JavaClass

            return JavaClass(node, parent)
        elif parent.project.language == lang.JAVASCRIPT:
            from .javascript.clazz import JavaScriptClass

            return JavaScriptClass(node, parent)
        elif parent.project.language == lang.PYTHON:
            from .python.clazz import PythonClass

            return PythonClass(node, parent)
        elif parent.project.language == lang.GO:
            from .go.clazz import GoClass

            return GoClass(node, parent)
        elif parent.project.language == lang.PHP:
            from .php.clazz import PHPClass

            return PHPClass(node, parent)
        elif parent.project.language == lang.RUBY:
            from .ruby.clazz import RubyClass

            return RubyClass(node, parent)
        elif parent.project.language == lang.RUST:
            from .rust.clazz import RustClass

            return RustClass(node, parent)
        elif parent.project.language == lang.SWIFT:
            from .swift.clazz import SwiftClass

            return SwiftClass(node, parent)
        elif parent.project.language == lang.CSHARP:
            from .csharp.clazz import CSharpClass

            return CSharpClass(node, parent)
        else:
            return Class(node, parent)

    @cached_property
    def name_node(self) -> Node:
        """
        The tree-sitter node representing the name of the class.
        """
        node = self.node.child_by_field_name("name")
        if node is None:
            raise ValueError(f"Class name node not found: {self.node}")
        return node

    @property
    def name(self) -> str:
        """
        The name of the class.
        """
        name_node = self.name_node
        assert name_node.text is not None
        return name_node.text.decode()

    @property
    def functions(self) -> list[Function]:
        """
        functions in the class.
        """
        functions = []
        for statement in self.statements:
            if isinstance(statement, Function):
                functions.append(statement)
            if isinstance(statement, BlockStatement):
                # If the statement is a block, we need to find all functions within it
                functions.extend(
                    statement.statements_by_types(self.language.FUNCTION_STATEMENTS)
                )
        return functions
