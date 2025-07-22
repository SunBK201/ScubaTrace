from ..parser import Parser
from .language import GO


class GoParser(Parser):
    def __init__(self):
        super().__init__(GO.tslanguage)
