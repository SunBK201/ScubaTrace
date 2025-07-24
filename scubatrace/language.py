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

    query_function = "(function_definition)@name"
    """
    The tree-sitter query to match function definitions.
    """

    query_identifier = "(identifier)@name"
    """
    The tree-sitter query to match identifiers.
    """

    query_return = "(return_statement)@name"
    """
    The tree-sitter query to match return statements.
    """

    query_call = "(call_expression)@name"
    """
    The tree-sitter query to match function calls.
    """

    jump_statements: list[str]
    """
    The tree-sitter AST types of jump statements.

    For example, in Python, this would include 'break', 'continue', 'return', etc.
    """

    loop_statements: list[str]
    """
    The tree-sitter AST types of loop statements.
    
    For example, in Python, this would include 'for', 'while', etc.
    """

    block_statements: list[str]
    """
    The tree-sitter AST types of block statements.

    For example, in Python, this would include 'if', 'for', 'while', etc.
    """

    simple_statements: list[str]
    """
    The tree-sitter AST types of simple statements.

    For example, in Python, this would include 'expression_statement', 'pass_statement', etc.
    """

    control_statements: list[str]
    """
    The tree-sitter AST types of control statements.

    For example, in Python, this would include 'if', 'elif', 'else', etc.
    """

    @staticmethod
    @abstractmethod
    def query_left_value(text: str) -> str:
        """
        Formats a tree-sitter query to match left values in the given text.
        """
        ...

    @classmethod
    def is_block_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a block statement.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a block statement, False otherwise.
        """
        return node.type in cls.block_statements

    @classmethod
    def is_simple_node(cls, node: Node) -> bool:
        """
        Checks if the given node is a simple statement.

        Args:
            node (Node): The tree-sitter node to check.

        Returns:
            bool: True if the node is a simple statement, False otherwise.
        """
        if node.parent is not None and node.parent.type in cls.simple_statements:
            return False
        return node.type in cls.simple_statements

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
