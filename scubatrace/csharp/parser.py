from ..parser import Parser
from .language import CSHARP


class CSharpParser(Parser):
    def __init__(self):
        super().__init__(CSHARP.tslanguage)
