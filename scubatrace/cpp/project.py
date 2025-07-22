from functools import cached_property

from ..project import Project
from . import language
from .parser import CParser


class CProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.C, enable_lsp)
        self._parser = CParser()

    @property
    def parser(self):
        return self._parser

    @cached_property
    def entry_point(self):
        for func in self.functions:
            if func.name == "main":
                return func
        return None
