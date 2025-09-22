import tree_sitter_java as tsjava
from tree_sitter import Language as TSLanguage

from ..language import Language


class JAVA(Language):
    extensions = ["java"]
    tslanguage = TSLanguage(tsjava.language())

    query_call = "(method_invocation)@name"
    query_argument = """
        (method_invocation
            arguments: (argument_list
                [
                    (field_access
                        field: (identifier)@name
                    )
                    (identifier)@name
                ]
            )
        )
    """
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
    query_function_parameter = """
        (formal_parameter
        	name: (identifier)@name
        )
    """

    query_package = "(package_declaration)@name"
    query_class = "(class_declaration)@name"

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    BLOCK_STATEMENTS = [
        "class_declaration",
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

    SIMPLE_STATEMENTS = [
        "expression_statement",
        "return_statement",
        "local_variable_declaration",
        "break_statement",
        "continue_statement",
        "yield_statement",
        "package_declaration",
        "import_declaration",
        "field_declaration",
    ]

    LOOP_STATEMENTS = [
        "for_statement",
        "while_statement",
        "do_statement",
        "enhanced_for_statement",
    ]

    CLASS_STATEMENTS = [
        "class_declaration",
        "interface_declaration",
    ]

    FUNCTION_STATEMENTS = [
        "method_declaration",
        "constructor_declaration",
    ]

    EXIT_STATEMENTS = [
        "return_statement",
    ]

    IF_STATEMENTS = [
        "if_statement",
    ]

    SWITCH_STATEMENTS = [
        "switch_expression",
    ]

    CONTINUE_STATEMENTS = [
        "continue_statement",
    ]

    BREAK_STATEMENTS = [
        "break_statement",
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
