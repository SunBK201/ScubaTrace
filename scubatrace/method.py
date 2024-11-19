from typing import TYPE_CHECKING

from tree_sitter import Node

from .function import Function

if TYPE_CHECKING:
    from .clazz import Class


class Method(Function):
    def __init__(self, node: Node, clazz: Class) -> None:
        super().__init__(node, clazz.file)
        self.clazz = clazz
