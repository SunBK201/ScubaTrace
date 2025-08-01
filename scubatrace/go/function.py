from __future__ import annotations

from functools import cached_property

from ..function import Function
from .statement import GoBlockStatement, Statement


class GoFunction(Function, GoBlockStatement):
    @cached_property
    def first_statement(self) -> Statement | None:
        for statement in self.statements:
            if statement.node_type != "defer_statement":
                return statement

    @cached_property
    def defer_statements(self) -> list[Statement]:
        return self.statements_by_type("defer_statement")
