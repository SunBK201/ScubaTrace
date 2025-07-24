from typing import Generator

from tree_sitter import Language as TSLanguage
from tree_sitter import Node, Tree
from tree_sitter import Parser as TSParser


class Parser:
    """
    A parser for a specific programming language using tree-sitter.
    """

    def __init__(self, language: TSLanguage) -> None:
        self.language = language
        self.parser = TSParser(language)

    def parse(self, code: str) -> Node:
        """
        Parses the given code and returns the root node of the tree-sitter ast.

        Args:
            code (str): The code to parse.

        Returns:
            Node: The root node of the tree-sitter AST.
        """
        return self.parser.parse(bytes(code, "utf-8")).root_node

    @staticmethod
    def traverse_tree(tree: Tree | Node) -> Generator[Node, None, None]:
        """
        Traverses the tree and yields all nodes in a depth-first manner.

        Args:
            tree (Tree | Node): The tree or node to traverse.

        Yields:
            Node: The current node in the traversal.
        """
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

    def query(self, target: str | Node, query_str: str) -> dict[str, list[Node]]:
        """
        Executes a tree-sitter query on the target and returns the captures.

        Args:
            target (str | Node): The target to query, either a string or a tree-sitter Node.
            query_str (str): The tree-sitter query to execute.

        Returns:
            dict[str, list[Node]]: A dictionary where keys are capture names and values are lists of nodes captured by the query.
        """
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
        """
        Executes a tree-sitter query on the target and returns the first capture.

        Args:
            target (str | Node): The target to query, either a string or a tree-sitter Node.
            query_str (str): The tree-sitter query to execute.

        Returns:
            Node | None: The first node captured by the query, or None if no captures are found.
        """
        captures = self.query(target, query_str)
        for nodes in captures.values():
            return nodes[0]
        return None

    def query_all(self, target: str | Node, query_str: str) -> list[Node]:
        """
        Executes a tree-sitter query on the target and returns all captures sorted by their start point.

        Args:
            target (str | Node): The target to query, either a code string or a tree-sitter Node.
            query_str (str): The tree-sitter query to execute.

        Returns:
            list[Node]: A list of all nodes captured by the query, sorted by their start point.
        """
        captures = self.query(target, query_str)
        results = []
        for nodes in captures.values():
            results.extend(nodes)
        return sorted(results, key=lambda node: node.start_point)

    def query_by_capture_name(
        self, target: str | Node, query_str: str, capture_name: str
    ) -> list[Node]:
        """
        Executes a tree-sitter query on the target and returns captures for a specific capture name.

        Args:
            target (str | Node): The target to query, either a code string or a tree-sitter Node.
            query_str (str): The tree-sitter query to execute.
            capture_name (str): The name of the capture to retrieve.

        Returns:
            list[Node]: A list of nodes captured by the query for the specified capture name.
        """
        captures = self.query(target, query_str)
        return captures.get(capture_name, [])
