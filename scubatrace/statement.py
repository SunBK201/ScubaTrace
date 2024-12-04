from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from .parser import c_parser

if TYPE_CHECKING:
    from .file import File
    from .function import Function


class Statement:
    def __init__(self, node: Node, parent: Function | File):
        self.node = node
        self.parent = parent

    def __str__(self) -> str:
        return self.signature

    @property
    def signature(self) -> str:
        return (
            self.parent.signature
            + "#"
            + str(self.start_line)
            + "#"
            + str(self.end_line)
        )

    @property
    def text(self) -> str:
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def start_line(self) -> int:
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        return self.node.end_point[0] + 1

    @property
    def length(self):
        return self.end_line - self.start_line + 1

    @property
    def file(self) -> File:
        if isinstance(self.parent, File):
            return self.parent
        return self.parent.file

    @property
    def pre_controls(self) -> list[Statement]: ...

    @property
    def post_controls(self) -> list[Statement]: ...


class CStatement(Statement):
    def __init__(self, node: Node, parent: Function | File):
        super().__init__(node, parent)

    @staticmethod
    def generater(
        node: Node, parent: Function | File
    ) -> Generator[Statement, None, None]:
        if node is None:
            yield from ()

        cursor = node.walk()
        if not cursor.goto_first_child():
            yield from ()
        while True:
            assert cursor.node is not None
            if c_parser.is_simple_statement(cursor.node):
                yield CSimpleStatement(cursor.node, parent)
            elif c_parser.is_block_statement(cursor.node):
                yield CBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break


class SimpleStatement(Statement):
    def __init__(self, node: Node, parent: Function | File):
        super().__init__(node, parent)


class BlockStatement(Statement):
    def __init__(self, node: Node, parent: Function | File):
        super().__init__(node, parent)

    @property
    def statements(self) -> list[Statement]: ...


class CSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: Function | File):
        super().__init__(node, parent)


class CBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: Function | File):
        super().__init__(node, parent)

    @property
    def statements(self) -> list[Statement]:
        return list(CStatement.generater(self.node, self.parent))
