from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING

import networkx as nx
from tree_sitter import Node

from . import language as lang
from .call import Call
from .statement import BlockStatement, Statement

if TYPE_CHECKING:
    from .file import File


class Function(BlockStatement):
    """
    Represents a function in the source code with various properties and methods to access its details.

    Attributes:
        node (Node): The AST node representing the function.
        file (File): The file in which the function is defined.
    """

    def __init__(self, node: Node, file: File, joern_id: str | None = None):
        super().__init__(node, file)
        self.joern_id = joern_id
        self._is_build_cfg = False

        self.callers_joern: list[Call] = []
        self.callees_joern: list[Call] = []

    @staticmethod
    def Function(node: Node, file: File):
        from .cpp.function import CFunction
        from .java.function import JavaFunction
        from .javascript.function import JavaScriptFunction
        from .python.function import PythonFunction

        if file.project.language == lang.C:
            return CFunction(node, file)
        elif file.project.language == lang.JAVA:
            return JavaFunction(node, file)
        elif file.project.language == lang.JAVASCRIPT:
            return JavaScriptFunction(node, file)
        elif file.project.language == lang.PYTHON:
            return PythonFunction(node, file)
        else:
            return Function(node, file)

    def __str__(self) -> str:
        return self.signature

    def set_joernid(self, joern_id: str):
        self.joern_id = joern_id

    @property
    def signature(self) -> str:
        return (
            self.file.signature
            + "#"
            + self.name
            + "#"
            + str(self.start_line)
            + "#"
            + str(self.end_line)
        )

    @property
    def lines(self) -> dict[int, str]:
        """
        Generates a dictionary mapping line numbers to their corresponding lines of text.


        Returns:
            dict[int, str]: A dictionary where the keys are line numbers (starting from `self.start_line`)
                            and the values are the lines of text from `self.text`.
        """
        return {
            i + self.start_line: line for i, line in enumerate(self.text.split("\n"))
        }

    @property
    def body_node(self) -> Node | None:
        """
        Retrieves the body node of the current node.

        Returns:
            Node | None: The body node if it exists, otherwise None.
        """
        return self.node.child_by_field_name("body")

    @property
    def body_start_line(self) -> int:
        """
        Returns the starting line number of the body of the node.

        If the body node is not defined, it returns the starting line number of the node itself.
        Otherwise, it returns the starting line number of the body node.

        Returns:
            int: The starting line number of the body or the node.
        """
        if self.body_node is None:
            return self.start_line
        else:
            return self.body_node.start_point[0] + 1

    @property
    def body_end_line(self) -> int:
        """
        Returns the ending line number of the body of the node.

        If the body_node attribute is None, it returns the end_line attribute.
        Otherwise, it returns the line number immediately after the end of the body_node.

        Returns:
            int: The ending line number of the body.
        """
        if self.body_node is None:
            return self.end_line
        else:
            return self.body_node.end_point[0] + 1

    @property
    def dot_text(self) -> str:
        return f"{self.name}#{self.file.name}#{self.start_line}"

    @cached_property
    @abstractmethod
    def parameter_lines(self) -> list[int]: ...

    @cached_property
    @abstractmethod
    def name_node(self) -> Node: ...

    @property
    @abstractmethod
    def name(self) -> str:
        name_node = self.name_node
        assert name_node.text is not None
        return name_node.text.decode()

    @cached_property
    @abstractmethod
    def accessible_functions(self) -> list[Function]:
        funcs = []
        for file in self.file.imports:
            for function in file.functions:
                funcs.append(function)
        for func in self.file.functions:
            funcs.append(func)
        return funcs

    @property
    def is_external(self) -> bool:
        return self.file.is_external

    @cached_property
    def calls(self) -> list[Statement]:
        parser = self.file.parser
        call_nodes = parser.query_all(self.node, self.language.query_call)
        calls = []
        for call_node in call_nodes:
            call_node_line = call_node.start_point[0] + 1
            calls.extend(self.statements_by_line(call_node_line))
        return calls

    @cached_property
    def callees(self) -> dict[Function | FunctionDeclaration, list[Statement]]:
        lsp = self.lsp
        callees = defaultdict(set[Statement])
        for call_stat in self.calls:
            for identifier in call_stat.identifiers:
                call_hierarchys = lsp.request_prepare_call_hierarchy(
                    self.file.relpath,
                    identifier.node.start_point[0],
                    identifier.node.start_point[1],
                )
                if len(call_hierarchys) == 0:
                    continue
                callee_def = lsp.request_definition(
                    call_stat.file.relpath,
                    identifier.node.start_point[0],
                    identifier.node.start_point[1],
                )
                if len(callee_def) == 0:
                    continue
                callee_def = callee_def[0]
                # external file
                if callee_def["uri"] not in self.file.project.files_uri:
                    if len(callee_def["uri"]) == 0:
                        continue
                    from .file import File

                    self.file.project.files_uri[callee_def["uri"]] = File.File(
                        callee_def["uri"],
                        self.file.project,
                    )
                callee_file = self.file.project.files_uri[callee_def["uri"]]
                callee_line = callee_def["range"]["start"]["line"] + 1
                callee_func = callee_file.function_by_line(callee_line)
                if callee_func is None:
                    declar = callee_file.lines[callee_line - 1]
                    callee_func = FunctionDeclaration(
                        identifier.text, declar, callee_file
                    )
                callees[callee_func].add(identifier.statement)
        callees = {k: list(v) for k, v in callees.items()}
        return callees

    @cached_property
    @abstractmethod
    def callers(self) -> dict[Function, list[Statement]]:
        lsp = self.lsp
        call_hierarchy = lsp.request_prepare_call_hierarchy(
            self.file.relpath,
            self.name_node.start_point[0],
            self.name_node.start_point[1],
        )
        if len(call_hierarchy) == 0:
            return {}
        call_hierarchy = call_hierarchy[0]
        calls = lsp.request_incoming_calls(call_hierarchy)
        callers = defaultdict(list[Statement])
        for call in calls:
            from_ = call["from_"]
            fromRanges = call["fromRanges"]
            caller_file = self.file.project.files_uri[from_["uri"]]
            for fromRange in fromRanges:
                callsite_line = fromRange["start"]["line"] + 1
                callsite_stats = caller_file.statements_by_line(callsite_line)
                for stat in callsite_stats:
                    if self.name in stat.text:
                        callers[stat.function].append(stat)
                        break
        return callers

    def __traverse_statements(self):
        stack = []
        for stat in self.statements:
            stack.append(stat)
            while stack:
                cur_stat = stack.pop()
                yield cur_stat
                if isinstance(cur_stat, BlockStatement):
                    stack.extend(reversed(cur_stat.statements))

    def statements_by_type(self, type: str, recursive: bool = False) -> list[Statement]:
        """
        Retrieves all statements of a given node type within the function.

        Args:
            type (str): The type of statement node to search for.
            recursive (bool): A flag to indicate whether to search recursively within nested blocks

        Returns:
            list[Statement]: A list of statements of the given type.
        """
        if recursive:
            return [
                stat for stat in self.__traverse_statements() if stat.node.type == type
            ]
        else:
            return [stat for stat in self.statements if stat.node.type == type]

    def slice_by_statements(
        self,
        statements: list[Statement],
        *,
        control_depth: int = 1,
        data_dependent_depth: int = 1,
        control_dependent_depth: int = 1,
    ) -> list[Statement]:
        """
        Slices the function into statements based on the provided statements.

        Args:
            statements (list[Statement]): A list of statements to slice the function by.

        Returns:
            list[Statement]: A list of statements that fall within the specified statements.
        """
        res = set()
        for stat in statements:
            for s in stat.walk_backward(depth=control_depth, base="control"):
                res.add(s)
            for s in stat.walk_forward(depth=control_depth, base="control"):
                res.add(s)
            for s in stat.walk_backward(
                depth=data_dependent_depth, base="data_dependent"
            ):
                res.add(s)
            for s in stat.walk_forward(
                depth=data_dependent_depth, base="data_dependent"
            ):
                res.add(s)
            for s in stat.walk_backward(
                depth=control_dependent_depth, base="control_dependent"
            ):
                res.add(s)
            for s in stat.walk_forward(
                depth=control_dependent_depth, base="control_dependent"
            ):
                res.add(s)
        return sorted(list(res), key=lambda x: x.node.start_byte)

    def slice_by_lines(
        self,
        lines: list[int],
        *,
        control_depth: int = 1,
        data_dependent_depth: int = 1,
        control_dependent_depth: int = 1,
    ) -> list[Statement]:
        statements = set()
        for line in lines:
            stats: list[Statement] = self.statements_by_line(line)
            if stats:
                statements.update(stats)

        return self.slice_by_statements(
            sorted(list(statements), key=lambda x: x.start_line),
            control_depth=control_depth,
            data_dependent_depth=data_dependent_depth,
            control_dependent_depth=control_dependent_depth,
        )

    @abstractmethod
    def _build_post_cfg(self, statements: list[Statement]): ...

    def _build_pre_cfg(self, statements: list[Statement]):
        for i in range(len(statements)):
            cur_stat = statements[i]
            for post_stat in cur_stat._post_control_statements:
                post_stat._pre_control_statements.append(cur_stat)
            if isinstance(cur_stat, BlockStatement):
                self._build_pre_cfg(cur_stat.statements)

    def build_cfg(self):
        self._build_post_cfg(self.statements)
        self._build_pre_cfg(self.statements)
        if len(self.statements) > 0:
            self.statements[0]._pre_control_statements.insert(0, self)
            self._post_control_statements = [self.statements[0]]
        else:
            self._post_control_statements = []
        self._is_build_cfg = True

    def __build_cfg_graph(self, graph: nx.DiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for post_stat in stat.post_controls:
                graph.add_node(post_stat.signature, label=post_stat.dot_text)
                graph.add_edge(stat.signature, post_stat.signature, label="CFG")
            if isinstance(stat, BlockStatement):
                self.__build_cfg_graph(graph, stat.statements)

    def __build_cdg_graph(self, graph: nx.MultiDiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for post_stat in stat.post_control_dependents:
                graph.add_node(post_stat.signature, label=post_stat.dot_text)
                graph.add_edge(
                    stat.signature,
                    post_stat.signature,
                    label="CDG",
                    color="green",
                )
            if isinstance(stat, BlockStatement):
                self.__build_cdg_graph(graph, stat.statements)

    def __build_ddg_graph(self, graph: nx.MultiDiGraph, statments: list[Statement]):
        for stat in statments:
            color = "blue" if isinstance(stat, BlockStatement) else "black"
            graph.add_node(stat.signature, label=stat.dot_text, color=color)
            for identifier, post_stats in stat.post_data_dependents.items():
                for post_stat in post_stats:
                    graph.add_node(post_stat.signature, label=post_stat.dot_text)
                    graph.add_edge(
                        stat.signature,
                        post_stat.signature,
                        label=f"DDG [{identifier.text}]",
                        color="red",
                    )
            if isinstance(stat, BlockStatement):
                self.__build_ddg_graph(graph, stat.statements)

    def export_cfg_dot(
        self, path: str, with_cdg: bool = False, with_ddg: bool = False
    ) -> nx.DiGraph:
        """
        Exports the CFG of the function to a DOT file.

        Args:
            path (str): The path to save the DOT file.
        """
        if not self._is_build_cfg:
            self.build_cfg()
        graph = nx.MultiDiGraph()
        graph.add_node("graph", bgcolor="ivory", splines="true")
        graph.add_node(
            "node",
            fontname="SF Pro Rounded, system-ui",
            shape="box",
            style="rounded",
            margin="0.5,0.1",
        )
        graph.add_node("edge", fontname="SF Pro Rounded, system-ui", arrowhead="vee")
        graph.add_node(self.signature, label=self.dot_text, color="red")
        graph.add_edge(self.signature, self.statements[0].signature, label="CFG")
        self.__build_cfg_graph(graph, self.statements)

        if with_cdg:
            self.__build_cdg_graph(graph, self.statements)

        if with_ddg:
            for identifier, post_stats in self.post_data_dependents.items():
                for post_stat in post_stats:
                    graph.add_node(post_stat.signature, label=post_stat.dot_text)
                    graph.add_edge(
                        self.signature,
                        post_stat.signature,
                        label=f"DDG [{identifier.text}]",
                        color="red",
                    )
            self.__build_ddg_graph(graph, self.statements)

        nx.nx_pydot.write_dot(graph, path)
        return graph


class FunctionDeclaration:
    def __init__(self, name: str, text: str, file: File):
        self.name = name
        self.text = text
        self.file = file

    def __hash__(self):
        return hash(self.signature)

    def __str__(self) -> str:
        return self.name

    @property
    def signature(self) -> str:
        return self.name + self.text + self.file.abspath

    @property
    def dot_text(self) -> str:
        return self.name
