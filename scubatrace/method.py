from typing import TYPE_CHECKING

from function import Function
from tree_sitter import Node

if TYPE_CHECKING:
    from .clazz import Class


class Method(Function):
    def __init__(self, node: Node, clazz: Class) -> None:
        super().__init__(node, clazz.file)
        self.clazz = clazz
