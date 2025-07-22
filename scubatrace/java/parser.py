from ..parser import Parser
from .language import JAVA


class JavaParser(Parser):
    def __init__(self):
        super().__init__(JAVA.tslanguage)
