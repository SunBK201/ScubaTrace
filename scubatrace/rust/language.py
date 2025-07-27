import tree_sitter_rust as tsrust
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUST(Language):
    extensions = ["rs"]
    tslanguage = TSLanguage(tsrust.language())

    query_function = "(function_item)@name"
    query_return = "(return_expression)@name"
    query_call = "(call_expression)@name"
    query_import_identifier = """
        (use_declaration
        	argument: (identifier)@name
        )
        (use_declaration
        	argument: (scoped_identifier
            	name: (identifier)@name
        )
    """

    query_class = "(struct_item)@name"

    jump_statements = [
        "break_expression",
        "continue_expression",
        "return_expression",
    ]

    block_statements = [
        "if_expression",
        "for_expression",
        "while_expression",
        "loop_expression",
    ]

    simple_statements = [
        "expression_statement",
        "let_declaration",
        "assignment_expression",
        "break_expression",
        "continue_expression",
        "return_expression",
    ]

    control_statements = [
        "if_expression",
        "for_expression",
    ]

    loop_statements = [
        "for_expression",
        "while_expression",
        "loop_expression",
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
