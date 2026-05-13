from functools import cached_property

from .. import joern
from ..project import Project
from . import language
from .parser import CSharpParser


class CSharpProject(Project):
    def __init__(
        self,
        path: str,
        enable_lsp: bool = True,
        joern_config: joern.JoernConfig | None = None,
    ):
        super().__init__(path, language.CSHARP, enable_lsp, joern_config)
        self._parser = CSharpParser()

    @property
    def parser(self):
        return self._parser

    @cached_property
    def entry_point(self):
        for func in self.functions:
            if func.name == "Main":
                return func
        return None
