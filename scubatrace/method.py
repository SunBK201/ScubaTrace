from tree_sitter import Node

from .clazz import Class
from .function import Function


class Method(Function):
    def __init__(self, node: Node, clazz: Class) -> None:
        super().__init__(node, clazz.file)
        self.clazz = clazz
