import tree_sitter_cpp as tspython
from tree_sitter import Language as TSLanguage

from ..language import Language


class PYTHON(Language):
    extensions = ["py"]
    tslanguage = TSLanguage(tspython.language())

    query_function = "(function_definition)@name"
    query_identifier = "(identifier)@name"
    query_class = "(class_definition)@name"
    query_import = "(import_statement)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "for_statement",
        "while_statement",
        "match_statement",
        "case_clause",
    ]

    simple_statements = [
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "while_statement",
        "match_statement",
    ]

    loop_statements = ["for_statement", "while_statement"]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (for_statement
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (augmented_assignment
                left: (identifier)@left
                (#eq? @left "{text}")
            )
        """
