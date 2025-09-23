import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language as TSLanguage

from ..language import Language


class CSHARP(Language):
    extensions = ["cs"]
    tslanguage = TSLanguage(tscsharp.language())

    query_call = "(invocation_expression)@name"
    query_import_identifier = """
        (using_directive
            [
                (identifier)@name
                (qualified_name
                    name: (identifier)@name
                )
            ]
        )
    """

    query_function_parameter = ""

    query_field_name = """
        (field_declaration
            (variable_declaration
                (variable_declarator
                    (identifier)@name
                )
            )
        )
        (property_declaration
            name: (identifier)@name
        )
    """

    query_class = "(class_declaration)@name"

    BLOCK_STATEMENTS = [
        "if_statement",
        "switch_statement",
        "switch_section",
        "while_statement",
        "do_statement",
        "for_statement",
        "foreach_statement",
    ]

    SIMPLE_STATEMENTS = [
        "expression_statement",
        "local_declaration_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
        "labeled_statement",
        "goto_statement",
    ]

    CLASS_STATEMENTS = [
        "class_declaration",
    ]

    FUNCTION_STATEMENTS = [
        "method_declaration",
    ]

    FIELD_STATEMENTS = [
        "field_declaration",
        "property_declaration",
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

    LOOP_STATEMENTS = [
        "while_statement",
        "do_statement",
        "for_statement",
        "foreach_statement",
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

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (assignment_expression
                left: (member_access_expression
                    name: (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (variable_declarator
                name: (identifier)@left
                (#eq? @left "{text}")
            )
        """

    @staticmethod
    def query_goto_label(label_name: str) -> str:
        return f"""
            (labeled_statement
                (identifier)@label
                (#eq? @label "{label_name}")
            )@labeled_statement
        """
