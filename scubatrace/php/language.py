import tree_sitter_php as tsphp
from tree_sitter import Language as TSLanguage

from ..language import Language


class PHP(Language):
    extensions = ["php"]
    tslanguage = TSLanguage(tsphp.language_php())

    query_identifier = "(name)@name"

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

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    BLOCK_STATEMENTS = [
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

    SIMPLE_STATEMENTS = [
        "expression_statement",
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
        "echo_statement",
        "namespace_definition",
        "named_label_statement",
    ]

    LOOP_STATEMENTS = [
        "for_statement",
        "foreach_statement",
        "while_statement",
        "do_statement",
    ]

    FUNCTION_STATEMENTS = [
        "function_definition",
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

    @staticmethod
    def query_goto_label(label_name: str) -> str:
        return f"""
            (named_label_statement
                (name)@label
                (#eq? @label "{label_name}")
            )@labeled_statement
        """
