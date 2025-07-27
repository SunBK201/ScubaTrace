import tree_sitter_php as tsphp
from tree_sitter import Language as TSLanguage

from ..language import Language


class PHP(Language):
    extensions = ["php"]
    tslanguage = TSLanguage(tsphp.language_php())

    query_identifier = "(name)@name"

    query_function = "(function_definition)@name"
    query_return = "(return_statement)@name"
    query_call = "(function_call_expression)@name"
    query_import_identifier = """
        (include_expression
            (string)@name
        )
        (include_once_expression
            (string)@name
        )
        (require_expression
            (string)@name
        )
        (require_once_expression
            (string)@name
        )
    """

    query_class = "(class_declaration)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "else_clause",
        "switch_statement",
        "case_statement",
        "for_statement",
        "foreach_statement",
        "while_statement",
        "do_statement",
        "try_statement",
    ]

    simple_statements = [
        "expression_statement",
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
        "echo_statement",
        "namespace_definition",
    ]

    control_statements = [
        "if_statement",
        "switch_statement",
        "for_statement",
        "foreach_statement",
        "while_statement",
        "do_statement",
        "named_label_statement",
    ]

    loop_statements = [
        "for_statement",
        "foreach_statement",
        "while_statement",
        "do_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (variable_name
                    (name)@left
                )
                (#eq? @left "{text}")
            )
            (update_expression
                argument: (variable_name
                    (name)@left
                )
                (#eq? @left "{text}")
            )
        """
