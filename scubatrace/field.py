from __future__ import annotations

from typing import TYPE_CHECKING

from tree_sitter import Node

if TYPE_CHECKING:
    from .clazz import Class


class Field:
    """
    A field (attribute or member variable) in a class.
    """

    node: Node
    """ The tree-sitter node representing the field. """

    clazz: Class
    """ The class that contains this field. """

    def __init__(self, node: Node, clazz: Class):
        self.node = node
        self.clazz = clazz

    @staticmethod
    def create(node: Node, clazz: Class) -> Field:
        """
        Factory function to create a Field instance based on the language of the file.

        Args:
            node (Node): The tree-sitter node representing the field.
            clazz (Class): The class containing the field.

        Returns:
            Field: An instance of a language-specific Field subclass corresponding to the file's language.
        """
        from . import language as lang

        if clazz.project.language == lang.C:
            from .cpp.field import CField

            return CField(node, clazz)
        elif clazz.project.language == lang.JAVA:
            from .java.field import JavaField

            return JavaField(node, clazz)
        elif clazz.project.language == lang.JAVASCRIPT:
            from .javascript.field import JavaScriptField

            return JavaScriptField(node, clazz)
        elif clazz.project.language == lang.PYTHON:
            from .python.field import PythonField

            return PythonField(node, clazz)
        elif clazz.project.language == lang.GO:
            from .go.field import GoField

            return GoField(node, clazz)
        elif clazz.project.language == lang.PHP:
            from .php.field import PHPField

            return PHPField(node, clazz)
        elif clazz.project.language == lang.RUBY:
            from .ruby.field import RubyField

            return RubyField(node, clazz)
        elif clazz.project.language == lang.RUST:
            from .rust.field import RustField

            return RustField(node, clazz)
        elif clazz.project.language == lang.SWIFT:
            from .swift.field import SwiftField

            return SwiftField(node, clazz)
        elif clazz.project.language == lang.CSHARP:
            from .csharp.field import CSharpField

            return CSharpField(node, clazz)
        else:
            return Field(node, clazz)

    @property
    def name(self) -> str:
        """
        The name of the field.

        Returns:
            str: The name of the field.
        """
        name_node = self.clazz.file.parser.query_oneshot(
            self.node, self.clazz.file.language.query_field_name
        )
        assert name_node is not None, "Field name node should not be None"
        assert name_node.text is not None, "Field name node text should not be None"
        return name_node.text.decode()
