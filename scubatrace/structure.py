from abc import abstractmethod

from tree_sitter import Node


class Struct:
    def __init__(self, node: Node):
        self.node = node

    @property
    @abstractmethod
    def name(self) -> str: ...


class CStruct(Struct):
    def __init__(self, node: Node):
        super().__init__(node)

    @property
    def name(self) -> str:
        node = self.node.child_by_field_name("name")
        assert node is not None and node.text is not None
        return node.text.decode()
