from functools import cached_property

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

    @cached_property
    def entry_point(self):
        for func in self.functions:
            if func.name == "main":
                return func
        return None

    @property
    def class_path(self) -> str:
        return self.path
