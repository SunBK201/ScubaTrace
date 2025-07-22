from __future__ import annotations

from functools import cached_property

from tree_sitter import Node

from ..function import Function
from ..statement import BlockStatement, Statement
from . import language
from .statement import CSharpBlockStatement, SimpleStatement


class CSharpFunction(Function, CSharpBlockStatement):
    @cached_property
    def name_node(self) -> Node: ...

    @cached_property
    def parameter_lines(self) -> list[int]: ...

    @cached_property
    def statements(self) -> list[Statement]: ...

    def __find_next_nearest_stat(
        self, stat: Statement, jump: int = 0
    ) -> Statement | None: ...

    def _build_post_cfg(self, statements: list[Statement]): ...
