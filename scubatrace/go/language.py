import tree_sitter_go as tsgo
from tree_sitter import Language as TSLanguage

from ..language import Language


class GO(Language):
    extensions = ["go"]
    tslanguage = TSLanguage(tsgo.language())

    query_function = "(function_declaration)@name"
    query_return = "(return_statement)@name"
    query_call = "(call_expression)@name"
    query_import_identifier = """
        (import_declaration
            (scoped_identifier
                name: (identifier)@name
            )
        )
        (import_declaration
            (identifier)@name
        )
    """

    query_package = "(package_clause)@name"
    query_class = "(type_declaration)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "for_statement",
        "expression_switch_statement",
        "select_statement",
        "communication_case",
    ]

    simple_statements = [
        "var_declaration",
        "const_declaration",
        "assignment_statement",
        "short_var_declaration",
        "return_statement",
        "break_statement",
        "continue_statement",
        "labeled_statement",
        "go_statement",
        "defer_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "expression_switch_statement",
        "select_statement",
        "labeled_statement",
    ]

    loop_statements = [
        "for_statement",
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
