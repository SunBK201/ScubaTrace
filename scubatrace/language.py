from abc import abstractmethod

from tree_sitter import Node

# from scubalspy import scubalspy_config


class Language:
    """
    Represents a programming language supported by ScubaTrace.
    """

    extensions: list[str]
    """
    The file extensions associated with the language.

    For example, Python would have ['.py'], C/C++ would have ['.c', '.cpp'], etc.
    """

    query_error = "(ERROR)@error"
    """
    The tree-sitter query to match error nodes.

    This is used to identify syntax errors in the code.
    """

    query_identifier = "(identifier)@name"
    """
    The tree-sitter query to match identifiers.
    """

    query_call: str
    """
    The tree-sitter query to match function calls.
    """

    query_argument: str
    """
    The tree-sitter query to match function call argument.
    """

    query_import_identifier: str
    """
    The tree-sitter query to match import identifiers.

    For example, in C/C++, this would match the `header.h` in `#include <header.h>`.
    """

    query_function_parameter: str
    """
    The tree-sitter query to match function parameters.
    """

    EXIT_STATEMENTS: list[str] = []
    """
    The tree-sitter AST types of exit statements.

    For example, in Python, this would include 'return'.
    """

    CLASS_STATEMENTS: list[str] = []

    FUNCTION_STATEMENTS: list[str] = []

    IF_STATEMENTS: list[str] = []

    SWITCH_STATEMENTS: list[str] = []

    CONTINUE_STATEMENTS: list[str] = []

    BREAK_STATEMENTS: list[str] = []

    GOTO_STATEMENTS: list[str] = []

    JUMP_STATEMENTS: list[str] = []

    LOOP_STATEMENTS: list[str] = []

    BLOCK_STATEMENTS: list[str] = []
    """
    The tree-sitter AST types of block statements.

    For example, in Python, this would include 'if', 'for', 'while', etc.
    """

    SIMPLE_STATEMENTS: list[str] = []
    """
    The tree-sitter AST types of simple statements.

    For example, in Python, this would include 'expression_statement', 'pass_statement', etc.
    """

    EXCLUDED_NODE_FIELDS: list[str] = []

    @staticmethod
    @abstractmethod
    def query_left_value(text: str) -> str:
        """
        Formats a tree-sitter query to match left values in the given text.
        """
        ...

    @staticmethod
    @abstractmethod
    def query_goto_label(label_name: str) -> str:
        """
        Formats a tree-sitter query to match goto statements with the given label name.
        """
        ...

    @classmethod
    def is_class_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a class definition.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a class definition, False otherwise.
        """
        return node.type in cls.CLASS_STATEMENTS

    @classmethod
    def is_function_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a function definition.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a function definition, False otherwise.
        """
        return node.type in cls.FUNCTION_STATEMENTS

    @classmethod
    def is_block_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a block statement.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a block statement, False otherwise.
        """
        return node.type in cls.BLOCK_STATEMENTS

    @classmethod
    def is_simple_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a simple statement.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a simple statement, False otherwise.
        """
        if node.parent is not None and node.parent.type in cls.SIMPLE_STATEMENTS:
            return False
        if not node.is_named:
            return False

        parent_node = node.parent
        if parent_node is not None:
            child_index = parent_node.named_children.index(node)
            node_field_name = parent_node.field_name_for_named_child(child_index)
            if (
                node_field_name is not None
                and node_field_name in cls.EXCLUDED_NODE_FIELDS
            ):
                return False

        return node.type in cls.SIMPLE_STATEMENTS

    # C = scubalspy_config.Language.C
    # JAVA = scubalspy_config.Language.JAVA
    # PYTHON = scubalspy_config.Language.PYTHON
    # JAVASCRIPT = scubalspy_config.Language.JAVASCRIPT
    # GO = scubalspy_config.Language.GO


from .cpp.language import C  # noqa: F401 E402
from .csharp.language import CSHARP  # noqa: F401 E402
from .go.language import GO  # noqa: F401 E402
from .java.language import JAVA  # noqa: F401 E402
from .javascript.language import JAVASCRIPT  # noqa: F401 E402
from .php.language import PHP  # noqa: F401 E402
from .python.language import PYTHON  # noqa: F401 E402
from .ruby.language import RUBY  # noqa: F401 E402
from .rust.language import RUST  # noqa: F401 E402
from .swift.language import SWIFT  # noqa: F401 E402
