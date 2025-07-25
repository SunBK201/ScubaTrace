import tree_sitter_javascript as tsjavascript
from tree_sitter import Language as TSLanguage

from ..language import Language


class JAVASCRIPT(Language):
    extensions = ["js"]
    tslanguage = TSLanguage(tsjavascript.language())

    query_function = """
    (function_declaration)@name
    (method_definition)@name
    """
    query_return = "(return_statement)@name"
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

    jump_statements = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "else_clause",
        "for_statement",
        "while_statement",
        "do_statement",
        "switch_case",
        "switch_default",
        "case_clause",
        "default_clause",
        "statement_block",
    ]

    simple_statements = [
        "variable_declaration",
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "while_statement",
        "do_statement",
        "switch_statement",
    ]

    loop_statements = ["for_statement", "while_statement", "do_statement"]

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
