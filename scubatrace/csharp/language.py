import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language as TSLanguage

from ..language import Language


class CSHARP(Language):
    extensions = ["cs"]
    tslanguage = TSLanguage(tscsharp.language())

    query_function = "(method_declaration)@name"
    query_return = "(return_statement)@name"
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

    query_class = "(class_declaration)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "switch_statement",
        "switch_section",
        "while_statement",
        "do_statement",
        "for_statement",
        "foreach_statement",
    ]

    simple_statements = [
        "expression_statement",
        "local_declaration_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
        "labeled_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "switch_statement",
        "switch_section",
        "labeled_statement",
    ]

    loop_statements = [
        "while_statement",
        "do_statement",
        "for_statement",
        "foreach_statement",
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
