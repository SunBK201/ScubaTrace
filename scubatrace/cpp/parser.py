from ..parser import Parser
from .language import C


class CParser(Parser):
    def __init__(self):
        super().__init__(C.tslanguage)
