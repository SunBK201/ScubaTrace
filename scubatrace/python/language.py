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
        "class_definition",
        "decorated_definition",
        "for_statement",
        "function_definition",
        "if_statement",
        "match_statement",
        "try_statement",
        "while_statement",
        "with_statement",
        "case_clause",
    ]

    simple_statements = [
        "assert_statement",
        "break_statement",
        "continue_statement",
        "delete_statement",
        "exec_statement",
        "expression_statement",
        "future_import_statement",
        "global_statement",
        "import_from_statement",
        "import_statement",
        "nonlocal_statement",
        "pass_statement",
        "print_statement",
        "raise_statement",
        "return_statement",
        "type_alias_statement",
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
