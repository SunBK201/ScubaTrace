import tree_sitter_swift as tsswift
from tree_sitter import Language as TSLanguage

from ..language import Language


class SWIFT(Language):
    extensions = ["swift"]
    tslanguage = TSLanguage(tsswift.language())

    query_return = """
    (control_transfer_statement)@name
    (#eq? @left "return")
    """
    query_call = "(call_expression)@name"
    query_import_identifier = """
        (import_declaration
            (identifier)@name
        )
    """

    query_function_parameter = ""

    query_field_name = """
        (property_declaration
            (pattern
                (simple_identifier)@name
            )
        )
        (variable_declaration
            (pattern_binding
                (pattern
                    (simple_identifier)@name
                )
            )
        )
    """

    query_class = "(class_declaration)@name"

    JUMP_STATEMENTS = [
        "control_transfer_statement",
    ]

    BLOCK_STATEMENTS = [
        "if_statement",
        "for_statement",
        "while_statement",
        "repeat_while_statement",
    ]

    SIMPLE_STATEMENTS = JUMP_STATEMENTS + [
        "import_declaration",
        "property_declaration",
        "call_expression",
        "assignment",
    ]

    LOOP_STATEMENTS = [
        "for_statement",
        "while_statement",
        "repeat_while_statement",
    ]

    CLASS_STATEMENTS = [
        "class_declaration",
    ]

    FUNCTION_STATEMENTS = [
        "function_declaration",
    ]

    FIELD_STATEMENTS = [
        "property_declaration",
        "variable_declaration",
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
        "control_transfer_statement",
    ]

    BREAK_STATEMENTS = [
        "control_transfer_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment
                target: (directly_assignable_expression
                    (simple_identifier)@left
                )
                (#eq? @left "{text}")
            )
            (function_declaration
                (parameter
                    name: (simple_identifier)@left
                )
                (#eq? @left "{text}")
            )
        """
