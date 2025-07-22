from ..project import Project
from . import language
from .parser import PHPParser


class PHPProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.PHP, enable_lsp)
        self._parser = PHPParser()

    @property
    def parser(self):
        return self._parser
