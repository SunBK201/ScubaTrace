from abc import abstractmethod

import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
from tree_sitter import Language as TSLanguage

# from scubalspy import scubalspy_config


class Language:
    extensions: list[str]

    query_error = "(ERROR)@error"

    query_function = "(function_definition)@name"
    query_identifier = "(identifier)@name"
    query_return = "(return_statement)@name"
    query_call = "(call_expression)@name"

    jump_statements: list[str]
    loop_statements: list[str]
    block_statements: list[str]
    simple_statements: list[str]
    control_statements: list[str]

    @staticmethod
    @abstractmethod
    def query_left_value(text) -> str: ...

    # C = scubalspy_config.Language.C
    # JAVA = scubalspy_config.Language.JAVA
    # PYTHON = scubalspy_config.Language.PYTHON
    # JAVASCRIPT = scubalspy_config.Language.JAVASCRIPT
    # GO = scubalspy_config.Language.GO


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


class JAVA(Language):
    extensions = ["java"]
    tslanguage = TSLanguage(tsjava.language())
    query_import = "(import_declaration(scoped_identifier)@name)"
    query_package = "(package_declaration)@name"
    query_class = "(class_declaration)@name"
    query_method = "(method_declaration)@name"
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
        "switch_statement",
    ]

    loop_statements = ["for_statement", "while_statement", "do_statement"]

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
        "if_statement",
        "for_statement",
        "while_statement",
        "match_statement",
        "case_clause",
    ]

    simple_statements = [
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
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


class JAVASCRIPT(Language):
    extensions = ["js"]
    tslanguage = TSLanguage(tsjavascript.language())

    query_function = "(function_declaration)@name"
    query_method = "(method_definition)@name"
    query_identifier = "(identifier)@name"
    query_import = "(import_statement)@name"
    query_export = "(export_statement)@name"
    query_call = "(call_expression)@name"
    query_class = "(class_declaration)@name"

    jump_statements = [
        "break_statement",
        "continue_statement",
        "return_statement",
    ]

    block_statements = [
        "if_statement",
        "else_clause",
        "for_statement",
        "while_statement",
        "do_statement",
        "switch_case",
        "switch_default",
        "case_clause",
        "default_clause",
        "statement_block",
    ]

    simple_statements = [
        "variable_declaration",
        "expression_statement",
        "return_statement",
        "break_statement",
        "continue_statement",
    ]

    control_statements = [
        "if_statement",
        "for_statement",
        "while_statement",
        "do_statement",
        "switch_statement",
    ]

    loop_statements = ["for_statement", "while_statement", "do_statement"]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment_expression
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (variable_declarator
                name: (identifier)@left
                (#eq? @left "{text}")
            )
        """


class GO(Language):
    extensions = ["go"]
