from ..parser import Parser
from .language import JAVASCRIPT


class JavaScriptParser(Parser):
    def __init__(self):
        super().__init__(JAVASCRIPT.tslanguage)
