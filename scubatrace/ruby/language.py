import tree_sitter_ruby as tsruby
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUBY(Language):
    extensions = ["rb"]
    tslanguage = TSLanguage(tsruby.language())

    query_call = "(call)@name"
    query_import_identifier = """
        (call
            method: (identifier)@call
            arguments: (argument_list
                (identifier)@name
            )
            (#eq? @call "require")
        )
    """

    query_function_parameter = ""

    query_field_name = """
        (assignment
            left: (instance_variable)@name
        )
        (assignment
            left: (class_variable)@name
        )
        (assignment
            left: (identifier)@name
        )
    """

    query_class = "(class)@name"

    JUMP_STATEMENTS = [
        "break",
        "next",
        "redo",
        "return",
    ]

    BLOCK_STATEMENTS = [
        "if",
        "unless",
        "case",
        "when",
        "for",
        "while",
        "until",
    ]

    SIMPLE_STATEMENTS = [
        "break",
        "next",
        "redo",
        "return",
        "call",
        "assignment",
    ]

    LOOP_STATEMENTS = [
        "for",
        "while",
        "until",
    ]

    CLASS_STATEMENTS = [
        "class",
    ]

    FUNCTION_STATEMENTS = [
        "method",
    ]

    FIELD_STATEMENTS = [
        "assignment",
    ]

    EXIT_STATEMENTS = [
        "return",
    ]

    IF_STATEMENTS = [
        "if",
        "unless",
    ]

    SWITCH_STATEMENTS = [
        "case",
    ]

    CONTINUE_STATEMENTS = [
        "next",
    ]

    BREAK_STATEMENTS = [
        "break",
    ]

    @staticmethod
    def query_left_value(text):
        return f"""
            (assignment
                left: (identifier)@left
                (#eq? @left "{text}")
            )
            (assignment
                left: (left_assignment_list
                    (identifier)@left
                )
                (#eq? @left "{text}")
            )
            (method_parameters
                (identifier)@left
                (#eq? @left "{text}")
            )
            (method_parameters
                (optional_parameter
                    name: (identifier)@left
                )
                (#eq? @left "{text}")
            )
        """
