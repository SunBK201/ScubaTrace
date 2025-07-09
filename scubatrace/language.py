import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
from tree_sitter import Language as TSLanguage

# from scubalspy import scubalspy_config


class Language:
    extensions: list[str]

    query_error = "(ERROR)@error"

    # C = scubalspy_config.Language.CPP
    # CPP = scubalspy_config.Language.CPP
    # JAVA = scubalspy_config.Language.JAVA
    # PYTHON = scubalspy_config.Language.PYTHON
    # JAVASCRIPT = scubalspy_config.Language.JAVASCRIPT
    # GO = scubalspy_config.Language.GO


class C(Language):
    extensions = ["c", "h", "cc"]
    tslanguage = TSLanguage(tsc.language())

    query_function = "(function_definition)@name"
    query_identifier = "(identifier)@name"
    query_return = "(return_statement)@name"
    query_call = "(call_expression)@name"
    query_struct = "(struct_specifier)@name"
    query_include = "(preproc_include)@name"

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

    loop_statements = ["for_statement", "while_statement", "do_statement", "for_range_loop"]

    def language(self):
        return C


class CPP(C):
    extensions = C.extensions + ["cpp", "hpp", "cxx"]
    tslanguage = TSLanguage(tscpp.language())
    query_class = "(class_specifier)@name"
    query_method = "(function_definition)@name"
    query_field = "(field_declaration)@name"


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


class GO(Language):
    extensions = ["go"]
