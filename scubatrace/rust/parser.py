from ..parser import Parser
from .language import RUST


class RustParser(Parser):
    def __init__(self):
        super().__init__(RUST.tslanguage)
