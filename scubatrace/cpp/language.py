import tree_sitter_cpp as tscpp
from tree_sitter import Language as TSLanguage

from ..language import Language


class C(Language):
    extensions = ["c", "h", "cc", "cpp", "cxx", "hxx", "hpp"]
    tslanguage = TSLanguage(tscpp.language())

    query_identifier = """
        (identifier)@name
        (field_identifier)@name
    """
    query_call = "(call_expression)@name"
    query_import_identifier = """
        (preproc_include
            path: [
                (system_lib_string)@name
                (string_literal)@name
            ]
        )
    """
    query_function_parameter = """
        (parameter_declaration
        	declarator: [
            	(identifier)@name
                (pointer_declarator
                	(identifier)@name
                )
                (pointer_declarator
                	(pointer_declarator
                		(identifier)@name
                    )
                )
                (pointer_declarator
                	(pointer_declarator
                        (pointer_declarator
                            (identifier)@name
                        )
                    )
                )
                (pointer_declarator
                    (pointer_declarator
                        (pointer_declarator
                            (pointer_declarator
                                (identifier)@name
                            )
                        )
                    )
                )
            ]
        )
    """

    query_struct = "(struct_specifier)@name"
    query_class = "(class_specifier)@name"
    query_field = "(field_declaration)@name"
    query_include = "(preproc_include)@name"

    query_global_statement = (
        "(declaration)@name"
        "(struct_specifier)@name"
        "(union_specifier)@name"
        "(type_definition)@name"
        "(preproc_def)@name"
    )

    BLOCK_STATEMENTS = [
        "if_statement",
        "for_statement",
        "for_range_loop",
        "while_statement",
        "do_statement",
        "switch_statement",
        "case_statement",
        "default_statement",
        "class_specifier",
        "field_declaration",
    ]

    SIMPLE_STATEMENTS = [
        "declaration",
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
        "goto_statement",
        "labeled_statement",
        "preproc_include",
        "preproc_def",
        "struct_specifier",
        "type_definition",
        "using_declaration",
    ]

    LOOP_STATEMENTS = [
        "for_statement",
        "for_range_loop",
        "while_statement",
        "do_statement",
    ]

    JUMP_STATEMENTS = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
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

    EXCLUDED_NODE_FIELDS = ["initializer"]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (assignment_expression
                left: (field_expression
                	argument: (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (assignment_expression
                left: (pointer_expression
                    argument: (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (init_declarator
                declarator: (identifier)@left
                (#eq? @left "{text}")
            )
            (init_declarator
                (pointer_declarator
                    declarator: (identifier)@left
                    (#eq? @left "{text}")
                )
            )
            (init_declarator
                (reference_declarator
                    (identifier)@left
                    (#eq? @left "{text}")
                )
            )
            (parameter_declaration
                declarator: (identifier)@left
                (#eq? @left "{text}")
            )
            (parameter_declaration
                declarator: (pointer_declarator
                    (identifier)@left
                )
                (#eq? @left "{text}")
            )
        """

    @staticmethod
    def query_goto_label(label_name: str) -> str:
        return f"""
            (labeled_statement
                label: (statement_identifier)@label
                (#eq? @label "{label_name}")
            )@labeled_statement
        """
