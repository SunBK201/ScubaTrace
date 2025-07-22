from ..project import Project
from . import language
from .parser import CSharpParser


class CSharpProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.CSHARP, enable_lsp)
        self._parser = CSharpParser()

    @property
    def parser(self):
        return self._parser
