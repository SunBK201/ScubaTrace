import tree_sitter_cpp as tsjava
from tree_sitter import Language as TSLanguage

from ..language import Language


class JAVA(Language):
    extensions = ["java"]
    tslanguage = TSLanguage(tsjava.language())

    query_function = query_method = "(method_declaration)@name"
    query_return = "(return_statement)@name"
    query_call = "(method_invocation)@name"
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

    query_package = "(package_declaration)@name"
    query_class = "(class_declaration)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "for_statement",
        "enhanced_for_statement",
        "while_statement",
        "do_statement",
        "switch_expression",
        "switch_block_statement_group",
        "try_statement",
        "try_with_resources_statement",
        "catch_clause",
    ]

    simple_statements = [
        "expression_statement",
        "return_statement",
        "local_variable_declaration",
        "break_statement",
        "continue_statement",
        "yield_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "enhanced_for_statement",
        "while_statement",
        "do_statement",
        "switch_expression",
    ]

    loop_statements = [
        "for_statement",
        "while_statement",
        "do_statement",
        "enhanced_for_statement",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (local_variable_declaration
                declarator: (variable_declarator)@left
                (#eq? @left "{text}")
            )
            (local_variable_declaration
                declarator: (variable_declarator
                    name: (identifier)@left
                )
                (#eq? @left "{text}")
            )
        """
