import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
from tree_sitter import Language as TSLanguage


class Language:
    extensions: list[str]

    query_error = "(ERROR)@error"


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

    loop_statements = ["for_statement", "while_statement", "do_statement"]

    def language(self):
        return C


class CPP(Language):
    extensions = C.extensions + ["cpp", "hpp", "cxx"]
    tslanguage = TSLanguage(tscpp.language())


class JAVA(Language):
    extensions = ["java"]
    tslanguage = TSLanguage(tsjava.language())


class PYTHON(Language):
    extensions = ["py"]


class JAVASCRIPT(Language):
    extensions = ["js"]


class GO(Language):
    extensions = ["go"]
