from ..project import Project
from . import language
from .parser import RustParser


class RustProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.RUST, enable_lsp)
        self._parser = RustParser()

    @property
    def parser(self):
        return self._parser
