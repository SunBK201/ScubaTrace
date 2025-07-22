from ..project import Project
from . import language
from .parser import GoParser


class GoProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.GO, enable_lsp)
        self._parser = GoParser()

    @property
    def parser(self):
        return self._parser
