from abc import abstractmethod
from typing import Generator

from tree_sitter import Language as TSLanguage
from tree_sitter import Node, Tree
from tree_sitter import Parser as TSParser

from . import language


class Parser:
    def __init__(self, language: TSLanguage) -> None:
        self.language = language
        self.parser = TSParser(language)

    def parse(self, code: str) -> Node:
        return self.parser.parse(bytes(code, "utf-8")).root_node

    @staticmethod
    def traverse_tree(tree: Tree | Node) -> Generator[Node, None, None]:
        cursor = tree.walk()

        visited_children = False
        while True:
            if not visited_children:
                yield cursor.node  # type: ignore
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break

    @abstractmethod
    @staticmethod
    def traverse_statements(tree: Tree | Node) -> Generator[Node, None, None]: ...

    def query(self, target: str | Node, query_str: str) -> dict[str, list[Node]]:
        if isinstance(target, str):
            node = self.parse(target)
        elif isinstance(target, Node):
            node = target
        else:
            raise ValueError("target must be a string or Node")
        query = self.language.query(query_str)
        captures = query.captures(node)
        return captures

    def query_oneshot(self, target: str | Node, query_str: str) -> Node | None:
        captures = self.query(target, query_str)
        for nodes in captures.values():
            return nodes[0]
        return None

    def query_all(self, target: str | Node, query_str: str) -> list[Node]:
        captures = self.query(target, query_str)
        results = []
        for nodes in captures.values():
            results.extend(nodes)
        return results

    def query_by_capture_name(
        self, target: str | Node, query_str: str, capture_name: str
    ) -> list[Node]:
        captures = self.query(target, query_str)
        return captures.get(capture_name, [])

    @abstractmethod
    @staticmethod
    def is_block_statement(node: Node) -> bool: ...

    @abstractmethod
    @staticmethod
    def is_simple_statement(node: Node) -> bool: ...


class CParser(Parser):
    def __init__(self):
        super().__init__(language.C.tslanguage)

    @staticmethod
    def is_block_statement(node: Node) -> bool:
        return node.type in language.C.block_statements

    @staticmethod
    def is_simple_statement(node: Node) -> bool: ...


c_parser = CParser()
