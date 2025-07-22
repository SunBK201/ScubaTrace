from ..project import Project
from . import language
from .parser import JavaScriptParser


class JavaScriptProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.JAVASCRIPT, enable_lsp)
        self._parser = JavaScriptParser()

    @property
    def parser(self):
        return self._parser
