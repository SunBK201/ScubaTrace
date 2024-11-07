from abc import abstractmethod
from typing import TYPE_CHECKING

import language
from tree_sitter import Node

if TYPE_CHECKING:
    from file import File
    from method import Method


class Class:
    def __init__(self, node: Node, file: File) -> None:
        self.node = node
        self.file = file

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
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def methods(self) -> list[Method]: ...

    @property
    @abstractmethod
    def fields(self) -> list[str]: ...
