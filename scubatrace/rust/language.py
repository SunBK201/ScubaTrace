import tree_sitter_rust as tsrust
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUST(Language):
    extensions = ["rs"]
    tslanguage = TSLanguage(tsrust.language())

    query_call = "(call_expression)@name(macro_invocation)@name"
    query_import_identifier = """
        (use_declaration
        	argument: (identifier)@name
        )
        (use_declaration
        	argument: (scoped_identifier
            	name: (identifier)@name
        )
    """

    query_function_parameter = ""

    query_field_name = """
        (field_declaration
            name: (field_identifier)@name
        )
    """

    query_class = "(struct_item)@name"

    JUMP_STATEMENTS = [
        "break_expression",
        "continue_expression",
        "return_expression",
    ]

    BLOCK_STATEMENTS = [
        "if_expression",
        "match_expression",
        "match_arm",
        "for_expression",
        "while_expression",
        "loop_expression",
    ]

    SIMPLE_STATEMENTS = [
        "let_declaration",
        "assignment_expression",
        "break_expression",
        "continue_expression",
        "return_expression",
        "macro_invocation",
        "enum_item",
        "struct_item",
    ]

    LOOP_STATEMENTS = [
        "for_expression",
        "while_expression",
        "loop_expression",
    ]

    CLASS_STATEMENTS = [
        "struct_item",
    ]

    FUNCTION_STATEMENTS = [
        "function_item",
    ]

    FIELD_STATEMENTS = ["field_declaration"]

    EXIT_STATEMENTS = [
        "return_expression",
    ]

    IF_STATEMENTS = [
        "if_expression",
    ]

    SWITCH_STATEMENTS = [
        "match_expression",
    ]

    CONTINUE_STATEMENTS = [
        "continue_expression",
    ]

    BREAK_STATEMENTS = [
        "break_expression",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
            	left: (identifier)@left
                (#eq? @left "{text}")
            )
            (assignment_expression
            	left: (field_expression
                	field: (field_identifier)@left
                )
                (#eq? @left "{text}")
            )
            (let_declaration
            	pattern: (identifier)@left
                (#eq? @left "{text}")
            )
        """
