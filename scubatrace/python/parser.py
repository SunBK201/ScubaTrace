from ..parser import Parser
from .language import PYTHON


class PythonParser(Parser):
    def __init__(self):
        super().__init__(PYTHON.tslanguage)
