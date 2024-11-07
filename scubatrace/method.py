from abc import abstractmethod
from typing import TYPE_CHECKING

import language
from function import Function
from tree_sitter import Node

if TYPE_CHECKING:
    from clazz import Class


class Method(Function):
    def __init__(self, node, clazz: Class) -> None:
        super().__init__(node, clazz.file)
        self.clazz = clazz
