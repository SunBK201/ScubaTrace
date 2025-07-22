from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from ..statement import BlockStatement, SimpleStatement

if TYPE_CHECKING:
    from ..file import File
    from ..function import Function
    from ..statement import Statement


class CSimpleStatement(SimpleStatement): ...


class CBlockStatement(BlockStatement):
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
            if self.is_simple_statement(cursor.node):
                yield CSimpleStatement(cursor.node, parent)
            elif self.is_block_statement(cursor.node):
                yield CBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if (
                    consequence_node is not None
                    and consequence_node.type == "compound_statement"
                ):  # if () { ... }
                    stats.extend(list(self._build_statements(consequence_node, self)))
                elif consequence_node is not None:  # if () ...;
                    stats.extend([CSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:  # else { ... }
                    stats.extend([CBlockStatement(else_clause_node, self)])
            case "else_clause":
                compound_node = None
                for child in self.node.children:
                    if child.type == "compound_statement":
                        compound_node = child
                if compound_node is not None:  # else { ... }
                    stats.extend(list(self._build_statements(compound_node, self)))
                else:  # else ...;
                    stats.extend(list(self._build_statements(self.node, self)))
            case "for_range_loop":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "while_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "do_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "switch_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._build_statements(body_node, self)))
                elif body_node is not None:
                    stats.extend([CSimpleStatement(body_node, self)])
            case "case_statement":
                get_compound = False
                for child in self.node.children:
                    if child.type in ["compound_statement"]:
                        stats.extend(list(self._build_statements(child, self)))
                        get_compound = True
                if not get_compound:
                    stats.extend(list(self._build_statements(self.node, self)))
            case _:
                stats.extend(list(self._build_statements(self.node, self)))
        return stats
