from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

if TYPE_CHECKING:
    from .file import File
    from .statement import Statement


class Identifier:
    def __init__(self, node: Node, statement: Statement):
        self.node = node
        self.statement = statement

    def __str__(self) -> str:
        return f"{self.signature}: {self.text}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Identifier) and self.signature == value.signature

    def __hash__(self):
        return hash(self.signature)

    @property
    def signature(self) -> str:
        return (
            self.file.signature
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
        return self.statement.file

    @property
    def function(self):
        if self.statement.function is None:
            return None
        if "Function" not in self.statement.function.__class__.__name__:
            return None
        return self.statement.function

    @property
    def references(self) -> Generator[Identifier, None, None]:
        func = self.function
        assert func is not None
        for identifier in func.identifiers:
            if identifier == self:
                continue
            if identifier.text == self.text:
                yield identifier
