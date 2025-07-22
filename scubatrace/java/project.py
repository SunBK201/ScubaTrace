from ..project import Project
from . import language
from .parser import JavaParser


class JavaProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.JAVA, enable_lsp)
        self._parser = JavaParser()

    @property
    def parser(self):
        return self._parser

    @property
    def class_path(self) -> str:
        return self.path
