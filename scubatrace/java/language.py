import tree_sitter_cpp as tsjava
from tree_sitter import Language as TSLanguage

from ..language import Language


class JAVA(Language):
    extensions = ["java"]
    tslanguage = TSLanguage(tsjava.language())
    query_import = "(import_declaration(scoped_identifier)@name)"
    query_package = "(package_declaration)@name"
    query_class = "(class_declaration)@name"
    query_function = query_method = "(method_declaration)@name"
    query_identifier = "(identifier)@name"

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
    ]

    simple_statements = [
        "expression_statement",
        "return_statement",
        "local_variable_declaration",
        "break_statement",
        "continue_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "enhanced_for_statement",
        "while_statement",
        "do_statement",
        "switch_expression",
    ]

    loop_statements = ["for_statement", "while_statement", "do_statement"]

    query_import_name = """
        (import_declaration
            (scoped_identifier
                name: (identifier)@name
            )
        )
        (import_declaration
            (identifier)@name
        )
    """

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
