from .. import joern
from ..project import Project
from . import language
from .parser import SwiftParser


class SwiftProject(Project):
    def __init__(
        self,
        path: str,
        enable_lsp: bool = True,
        joern_config: joern.JoernConfig | None = None,
    ):
        super().__init__(path, language.SWIFT, enable_lsp, joern_config)
        self._parser = SwiftParser()

    @property
    def parser(self):
        return self._parser
