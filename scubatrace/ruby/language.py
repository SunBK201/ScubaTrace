import tree_sitter_ruby as tsruby
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUBY(Language):
    extensions = ["rb"]
    tslanguage = TSLanguage(tsruby.language())

    query_function = "(method)@name"
    query_return = "(return)@name"
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

    query_class = "(class)@name"

    jump_statements = [
        "break",
        "next",
        "redo",
        "return",
    ]

    block_statements = [
        "if",
        "unless",
        "case",
        "when",
        "for",
        "while",
        "until",
    ]

    simple_statements = [
        "break",
        "next",
        "redo",
        "return",
        "call",
        "assignment",
    ]

    control_statements = [
        "if",
        "unless",
        "case",
        "for",
        "while",
        "until",
    ]

    loop_statements = [
        "for",
        "while",
        "until",
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
