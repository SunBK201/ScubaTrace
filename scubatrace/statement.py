from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from .parser import c_parser

if TYPE_CHECKING:
    from .file import File
    from .function import Function


class Statement:
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        self.node = node
        self.parent = parent
        self._post_statements = []
        self._pre_statements = []

    def __str__(self) -> str:
        return f"{self.signature}: {self.text}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Statement) and self.signature == value.signature

    @property
    def signature(self) -> str:
        return (
            self.parent.signature
            + "line"
            + str(self.start_line)
            + "-"
            + str(self.end_line)
            + "col"
            + str(self.start_column)
            + "-"
            + str(self.end_column)
        )

    @property
    def text(self) -> str:
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def dot_text(self) -> str:
        """
        escape the text ':' for dot
        """
        return '"' + self.text.replace('"', '\\"') + '"'

    @property
    def start_line(self) -> int:
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        return self.node.end_point[0] + 1

    @property
    def start_column(self) -> int:
        return self.node.start_point[1] + 1

    @property
    def end_column(self) -> int:
        return self.node.end_point[1] + 1

    @property
    def length(self):
        return self.end_line - self.start_line + 1

    @property
    def file(self) -> File:
        if isinstance(self.parent, File):
            return self.parent
        return self.parent.file

    @property
    def function(self):
        cur = self
        while "Function" not in cur.__class__.__name__:
            cur = cur.parent  # type: ignore
            if "File" in cur.__class__.__name__:
                return None
        return cur

    @property
    def post_controls(self) -> list[Statement]:
        func = self.function
        if func is None:
            return []
        assert "Function" in func.__class__.__name__
        if not func._is_build_cfg:  # type: ignore
            func.build_cfg()  # type: ignore
        return self._post_statements

    @post_controls.setter
    def post_controls(self, stats: list[Statement]):
        self._post_statements = stats

    @property
    def pre_controls(self) -> list[Statement]:
        func = self.function
        if func is None:
            return []
        assert "Function" in func.__class__.__name__
        if not func._is_build_cfg:  # type: ignore
            func.build_cfg()  # type: ignore
        return self._pre_statements

    @pre_controls.setter
    def pre_controls(self, stats: list[Statement]):
        self._pre_statements = stats


class CStatement(Statement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @staticmethod
    def generater(
        node: Node, parent: BlockStatement | Function | File
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
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)


class BlockStatement(Statement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @property
    def dot_text(self) -> str:
        """
        return only the first line of the text
        """
        return '"' + self.text.split("\n")[0].replace('"', '\\"') + '"'

    @cached_property
    def statements(self) -> list[Statement]: ...

    def __getitem__(self, index: int) -> Statement:
        return self.statements[index]


class CSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)


class CBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def statements(self) -> list[Statement]:
        if self.node.type in ["compound_statement"]:
            return list(CStatement.generater(self.node, self))
        else:
            for child in self.node.children:
                if child.type in ["compound_statement"]:
                    return list(CStatement.generater(child, self))
            return list(CStatement.generater(self.node, self))
