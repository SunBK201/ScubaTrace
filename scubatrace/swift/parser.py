from ..parser import Parser
from .language import SWIFT


class SwiftParser(Parser):
    def __init__(self):
        super().__init__(SWIFT.tslanguage)
