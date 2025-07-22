import tree_sitter_cpp as tscpp
from tree_sitter import Language as TSLanguage

from ..language import Language


class C(Language):
    extensions = ["c", "h", "cc", "cpp", "cxx", "hxx", "hpp"]
    tslanguage = TSLanguage(tscpp.language())

    query_function = "(function_definition)@name"
    query_identifier = "(identifier)@name"
    query_return = "(return_statement)@name"
    query_call = "(call_expression)@name"
    query_struct = "(struct_specifier)@name"
    query_class = "(class_specifier)@name"
    query_method = "(function_definition)@name"
    query_field = "(field_declaration)@name"
    query_include = "(preproc_include)@name"
    query_global_statement = (
        "(declaration)@name"
        "(struct_specifier)@name"
        "(union_specifier)@name"
        "(type_definition)@name"
        "(preproc_def)@name"
    )

    block_statements = [
        "if_statement",
        "for_statement",
        "for_range_loop",
        "while_statement",
        "do_statement",
        "switch_statement",
        "case_statement",
        "default_statement",
        "else_clause",
    ]

    simple_statements = [
        "declaration",
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
        "goto_statement",
        "binary_expression",
        "unary_expression",
        "labeled_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "for_range_loop",
        "while_statement",
        "do_statement",
        "switch_statement",
        "labeled_statement",
        "condition_clause",
    ]

    jump_statements = [
        "break_statement",
        "continue_statement",
        "goto_statement",
        "return_statement",
    ]

    loop_statements = [
        "for_statement",
        "while_statement",
        "do_statement",
        "for_range_loop",
    ]

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
