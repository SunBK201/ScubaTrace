from abc import abstractmethod

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


from .cpp.language import C
from .java.language import JAVA
from .javascript.language import JAVASCRIPT
from .python.language import PYTHON
