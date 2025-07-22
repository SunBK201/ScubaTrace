from ..project import Project
from . import language
from .parser import RubyParser


class RubyProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.RUBY, enable_lsp)
        self._parser = RubyParser()

    @property
    def parser(self):
        return self._parser
