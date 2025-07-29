import tree_sitter_javascript as tsjavascript
from tree_sitter import Language as TSLanguage

from ..language import Language


class JAVASCRIPT(Language):
    extensions = ["js"]
    tslanguage = TSLanguage(tsjavascript.language())

    query_call = "(call_expression)@name"
    query_import = "(import_statement)@name"
    query_import_identifier = """
    (call_expression
        function: [
            (identifier)@require
            (import)
        ]
        arguments: (arguments
            (string)@name
        )
        (#eq? @require "require")
    )
    (import_statement
        source: (string)@name
    )
    """

    query_class = "(class_declaration)@name"

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    BLOCK_STATEMENTS = [
        "if_statement",
        "for_statement",
        "while_statement",
        "do_statement",
        "switch_case",
        "switch_default",
        "case_clause",
        "default_clause",
    ]

    SIMPLE_STATEMENTS = [
        "variable_declaration",
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
    ]

    LOOP_STATEMENTS = ["for_statement", "while_statement", "do_statement"]

    FUNCTION_STATEMENTS = [
        "function_declaration",
        "method_definition",
    ]

    EXIT_STATEMENTS = [
        "return_statement",
    ]

    IF_STATEMENTS = [
        "if_statement",
    ]

    SWITCH_STATEMENTS = [
        "switch_statement",
    ]

    CONTINUE_STATEMENTS = [
        "continue_statement",
    ]

    BREAK_STATEMENTS = [
        "break_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (variable_declarator
                name: (identifier)@left
                (#eq? @left "{text}")
            )
        """
