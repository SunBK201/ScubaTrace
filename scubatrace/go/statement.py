from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from ..statement import BlockStatement, SimpleStatement

if TYPE_CHECKING:
    from ..file import File
    from ..function import Function
    from ..statement import Statement


class GoSimpleStatement(SimpleStatement): ...


class GoBlockStatement(BlockStatement):
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
                yield GoSimpleStatement(cursor.node, parent)
            elif self.language.is_block_node(cursor.node):
                yield GoBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if consequence_node is not None and consequence_node.type == "block":
                    stats.extend(list(self._build_statements(consequence_node, self)))
                elif consequence_node is not None:  # if () ...;
                    stats.extend([GoSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:  # if () { ... } else if () { ... }
                    stats.extend([GoBlockStatement(else_clause_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    if self.language.is_simple_node(body_node):
                        stats.extend([GoSimpleStatement(body_node, self)])
                    elif self.language.is_block_node(body_node):
                        stats.extend([GoBlockStatement(body_node, self)])
            case _:
                stats.extend(list(self._build_statements(self.node, self)))
        return stats
