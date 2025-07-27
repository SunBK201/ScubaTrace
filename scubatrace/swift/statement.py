from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from ..statement import BlockStatement, SimpleStatement

if TYPE_CHECKING:
    from ..file import File
    from ..function import Function
    from ..statement import Statement


class SwiftSimpleStatement(SimpleStatement): ...


class SwiftBlockStatement(BlockStatement):
    def _build_statements(
        self,
        node: Node,
        parent: BlockStatement | Function | File,
    ) -> Generator[Statement, None, None]:
        cursor = node.walk()
        if cursor.node is not None:
            if not cursor.goto_first_child():
                yield from ()
        while True:
            assert cursor.node is not None
            if self.language.is_simple_node(cursor.node):
                yield SwiftSimpleStatement(cursor.node, parent)
            elif self.language.is_block_node(cursor.node):
                yield SwiftBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.file.parser.query_oneshot(
                    self.node, "(statements)@name"
                )
                if consequence_node is not None:
                    stats.extend(list(self._build_statements(consequence_node, self)))
                else_clause_node = self.node.child_by_field_name("if_statement")
                if else_clause_node is not None:
                    stats.extend([SwiftBlockStatement(else_clause_node, self)])
            case "for_statement" | "while_statement" | "repeat_while_statement":
                body_node = self.node.child_by_field_name("statements")
                if body_node is not None:
                    stats.extend(list(self._build_statements(body_node, self)))
            case _:
                stats.extend(list(self._build_statements(self.node, self)))
        return stats
