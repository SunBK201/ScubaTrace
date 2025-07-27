import tree_sitter_swift as tsswift
from tree_sitter import Language as TSLanguage

from ..language import Language


class SWIFT(Language):
    extensions = ["swift"]
    tslanguage = TSLanguage(tsswift.language())

    query_function = "(function_declaration)@name"
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

    query_class = "(class_declaration)@name"

    jump_statements = [
        "control_transfer_statement",
    ]

    block_statements = [
        "if_statement",
        "for_statement",
        "while_statement",
        "repeat_while_statement",
    ]

    simple_statements = jump_statements + [
        "import_declaration",
        "property_declaration",
        "call_expression",
        "assignment",
    ]

    control_statements = block_statements

    loop_statements = [
        "for_statement",
        "while_statement",
        "repeat_while_statement",
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
