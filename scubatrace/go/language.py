import tree_sitter_go as tsgo
from tree_sitter import Language as TSLanguage

from ..language import Language


class GO(Language):
    extensions = ["go"]
    tslanguage = TSLanguage(tsgo.language())

    query_call = "(call_expression)@name"
    query_argument = """
        (call_expression
            arguments: (argument_list
                [
                    (selector_expression
                        field: (field_identifier)@name
                    )
                    (identifier)@name
                ]
            )
        )
    """
    query_import_identifier = """
        (import_spec
            path: (interpreted_string_literal)@name
        )
    """

    query_function_parameter = ""

    query_field_name = """
        (field_declaration
            (field_identifier)@name
        )
    """

    query_package = "(package_clause)@name"
    query_class = "(type_declaration)@name"

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    BLOCK_STATEMENTS = [
        "if_statement",
        "for_statement",
        "expression_switch_statement",
        "select_statement",
        "communication_case",
    ]

    SIMPLE_STATEMENTS = [
        "var_declaration",
        "const_declaration",
        "expression_statement",
        "assignment_statement",
        "short_var_declaration",
        "return_statement",
        "break_statement",
        "continue_statement",
        "labeled_statement",
        "go_statement",
        "defer_statement",
        "type_declaration",
        "package_clause",
    ]

    LOOP_STATEMENTS = [
        "for_statement",
    ]

    CLASS_STATEMENTS = [
        "type_declaration",
    ]

    FUNCTION_STATEMENTS = [
        "function_declaration",
    ]

    FIELD_STATEMENTS = []

    EXIT_STATEMENTS = [
        "return_statement",
    ]

    IF_STATEMENTS = [
        "if_statement",
    ]

    SWITCH_STATEMENTS = [
        "expression_switch_statement",
    ]

    CONTINUE_STATEMENTS = [
        "continue_statement",
    ]

    BREAK_STATEMENTS = [
        "break_statement",
    ]

    GOTO_STATEMENTS = [
        "goto_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_statement
                left: (expression_list
                    (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (assignment_statement
                left: (expression_list
                    (selector_expression
                        field: (field_identifier)@left
                    )
                    (#eq? @left "{text}")
                )
            )
            (short_var_declaration
                left: (expression_list)@left
                (#eq? @left "{text}")
            )
            (var_declaration
                (var_spec
                    name: (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (const_declaration
                (const_spec
                    name: (identifier)@left
                )
                (#eq? @left "{text}")
            )
        """

    @staticmethod
    def query_goto_label(label_name: str) -> str:
        return f"""
            (labeled_statement
                label: (label_name)@label
                (#eq? @label "{label_name}")
            )@labeled_statement
        """
