from ..project import Project
from . import language
from .parser import PythonParser


class PythonProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.PYTHON, enable_lsp)
        self._parser = PythonParser()

    @property
    def parser(self):
        return self._parser
