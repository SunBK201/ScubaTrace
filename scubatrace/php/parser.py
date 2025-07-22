from ..parser import Parser
from .language import PHP


class PHPParser(Parser):
    def __init__(self):
        super().__init__(PHP.tslanguage)
