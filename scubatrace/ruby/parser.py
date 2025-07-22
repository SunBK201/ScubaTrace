from ..parser import Parser
from .language import RUBY


class RubyParser(Parser):
    def __init__(self):
        super().__init__(RUBY.tslanguage)
