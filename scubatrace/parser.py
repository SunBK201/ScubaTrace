import language
from tree_sitter import Language as TSLanguage
from tree_sitter import Node
from tree_sitter import Parser as TSParser


class Parser:
    def __init__(self, language: TSLanguage) -> None:
        self.language = language
        self.parser = TSParser(language)

    def parse(self, code: str) -> Node:
        return self.parser.parse(bytes(code, "utf-8")).root_node

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

    def query_by_capture_name(self, target: str | Node, query_str: str, capture_name: str) -> list[Node]:
        captures = self.query(target, query_str)
        return captures.get(capture_name, [])


class CParser(Parser):
    def __init__(self):
        super().__init__(language.C.tslanguage)


c_parser = CParser()
