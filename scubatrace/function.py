from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

import networkx as nx
from tree_sitter import Node

from . import language
from .call import Call
from .parser import cpp_parser
from .statement import (
    BlockStatement,
    CBlockStatement,
    JavaScriptBlockStatement,
    PythonBlockStatement,
    SimpleStatement,
    Statement,
)

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

        self.callers: list[Call] = []
        self.callees: list[Call] = []

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

    @cached_property
    @abstractmethod
    def parameter_lines(self) -> list[int]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @cached_property
    @abstractmethod
    def accessible_functions(self) -> list[Function]: ...

    @cached_property
    @abstractmethod
    def calls(self) -> list[Statement]: ...

    # @cached_property
    # @abstractmethod
    # def callees(self) -> dict[Function, list[Statement]]:
    #     lsp = self.file.project.lsp
    #     lsp.request_document_symbols(self.file.relpath)  # preload symbols
    #     caller = lsp.request_prepare_call_hierarchy(
    #         self.file.relpath,
    #         self.start_line - 1,
    #         self.start_column - 1,
    #     )
    #     if len(caller) == 0:
    #         return {}
    #     caller = caller[0]
    #     calls = lsp.request_outgoing_calls(caller)
    #     for call in calls:
    #         to = call["to"]
    #         fromRanges = call["fromRanges"]
    #         uri = to["uri"]
    #         callee_line = to["range"]["start"]["line"]

    # @cached_property
    # @abstractmethod
    # def callers(self) -> dict[Function, list[Statement]]: ...

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


class CFunction(Function, CBlockStatement):
    def __init__(self, node: Node, file):
        super().__init__(node, file)

    @property
    def name(self) -> str:
        name_node = self.node.child_by_field_name("declarator")
        while name_node is not None and name_node.type not in {
            "identifier",
            "operator_name",
            "type_identifier",
        }:
            all_temp_name_node = name_node
            if (
                name_node.child_by_field_name("declarator") is None
                and name_node.type == "reference_declarator"
            ):
                for temp_node in name_node.children:
                    if temp_node.type == "function_declarator":
                        name_node = temp_node
                        break
            if name_node.child_by_field_name("declarator") is not None:
                name_node = name_node.child_by_field_name("declarator")
            # int *a()
            if (
                name_node is not None
                and name_node.type == "field_identifier"
                and name_node.child_by_field_name("declarator") is None
            ):
                break
            if name_node == all_temp_name_node:
                break
        assert name_node is not None
        assert name_node.text is not None
        return name_node.text.decode()

    @cached_property
    def parameter_lines(self) -> list[int]:
        declarator_node = self.node.child_by_field_name("declarator")
        if declarator_node is None:
            return [self.start_line]
        param_node = declarator_node.child_by_field_name("parameters")
        if param_node is None:
            return [self.start_line]
        param_node_start_line = param_node.start_point[0] + 1
        param_node_end_line = param_node.end_point[0] + 1
        return list(range(param_node_start_line, param_node_end_line + 1))

    def __find_next_nearest_stat(
        self, stat: Statement, jump: int = 0
    ) -> Statement | None:
        stat_type = stat.node.type
        if stat_type == "return_statement":
            return None

        if jump == -1:
            jump = 0x3F3F3F
        while (
            jump > 0
            and stat.parent is not None
            and isinstance(stat.parent, BlockStatement)
        ):
            stat = stat.parent
            jump -= 1

        parent_statements = stat.parent.statements
        index = parent_statements.index(stat)
        if (
            index < len(parent_statements) - 1
            and parent_statements[index + 1].node.type != "else_clause"
        ):
            return parent_statements[index + 1]
        else:
            if isinstance(stat.parent, Function):
                return None
            assert isinstance(stat.parent, BlockStatement)
            if stat.parent.node.type in language.C.loop_statements:
                return stat.parent
            else:
                return self.__find_next_nearest_stat(stat.parent)

    def _build_post_cfg(self, statements: list[Statement]):
        for i in range(len(statements)):
            cur_stat = statements[i]
            type = cur_stat.node.type
            next_stat = self.__find_next_nearest_stat(cur_stat)
            next_stat = [next_stat] if next_stat is not None else []

            if isinstance(cur_stat, BlockStatement):
                child_statements = cur_stat.statements
                self._build_post_cfg(child_statements)
                if len(child_statements) > 0:
                    match type:
                        case "if_statement":
                            else_clause = cur_stat.statements_by_type("else_clause")
                            if len(else_clause) == 0:
                                cur_stat._post_control_statements = [
                                    child_statements[0]
                                ] + next_stat
                            else:
                                if len(child_statements) == 1:
                                    cur_stat._post_control_statements = list(
                                        set([else_clause[0]] + next_stat)
                                    )
                                else:
                                    cur_stat._post_control_statements = list(
                                        set([child_statements[0], else_clause[0]])
                                    )
                        case "else_clause":
                            cur_stat._post_control_statements = [child_statements[0]]
                        case _:
                            cur_stat._post_control_statements = [
                                child_statements[0]
                            ] + next_stat
                else:
                    cur_stat._post_control_statements = next_stat
            elif isinstance(cur_stat, SimpleStatement):
                match type:
                    case "continue_statement":
                        # search for the nearest loop statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type not in language.C.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            cur_stat._post_control_statements.append(loop_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case "break_statement":
                        # search for the nearest loop or switch statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.C.loop_statements + ["switch_statement"]
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            next_loop_stat = self.__find_next_nearest_stat(loop_stat)
                            cur_stat._post_control_statements = (
                                [next_loop_stat] if next_loop_stat else []
                            )
                        else:
                            cur_stat._post_control_statements = next_stat
                    case "goto_statement":
                        goto_label = cur_stat.node.child_by_field_name("label")
                        assert goto_label is not None and goto_label.text is not None
                        label_name = goto_label.text.decode()
                        label_stat = None
                        for stat in self.statements_by_type(
                            "labeled_statement", recursive=True
                        ):
                            label_identifier_node = stat.node.child_by_field_name(
                                "label"
                            )
                            assert (
                                label_identifier_node is not None
                                and label_identifier_node.text is not None
                            )
                            label_identifier = label_identifier_node.text.decode()
                            if label_identifier == label_name:
                                label_stat = stat
                                break
                        if label_stat is not None:
                            cur_stat._post_control_statements.append(label_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case _:
                        cur_stat._post_control_statements = next_stat

    @cached_property
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(self._statements_builder(self.body_node, self))

    @cached_property
    def calls(self):  # -> list[Statement]:
        nodes = cpp_parser.query_all(self.node, language.C.query_call)
        calls: dict[Node, str] = {
            node: node.text.decode() for node in nodes if node.text is not None
        }
        stmts = []
        call_funcs: dict[Node, str] = {}
        for call_node in calls:
            func = call_node.child_by_field_name("function")
            assert func is not None
            for child in func.children:
                if child.type == "identifier" and child.text is not None:
                    call_funcs[call_node] = child.text.decode()
                    break

        for call in call_funcs.copy():
            accessible = False
            for func in self.accessible_functions:
                if func == call_funcs[call]:
                    accessible = True
                    break
            if not accessible:
                call_funcs.pop(call)

        for node in call_funcs:
            for stmt in self.statements:
                if (
                    stmt.node.start_point[0] == node.start_point[0]
                    and stmt.node.text == node.text
                ):
                    stmts.append(stmt)
                    break

        return stmts

    # @cached_property
    # def callers(self):  # -> dict[Function, list[Statement]]
    #     callers = {}
    #     for file in self.file.project.files:
    #         for func in self.file.project.files[file].functions:
    #             if self in func.callees:
    #                 for stmt in func.callees[self]:
    #                     try:
    #                         callers[func].append(stmt)
    #                     except Exception:
    #                         callers[func] = [stmt]
    #     return callers

    # @cached_property
    # def callees(self):  # -> dict[Function, list[Statement]]
    #     def get_callee_stmt(statements, callee):
    #         for stmt in statements:
    #             if isinstance(stmt, SimpleStatement):
    #                 if stmt.node.start_point[0] == callee.start_point[0]:
    #                     stmt_calls = c_parser.query_all(
    #                         stmt.node, language.C.query_call
    #                     )
    #                     for stmt_call in stmt_calls:
    #                         if stmt_call.text == callee.text:
    #                             return stmt
    #             elif isinstance(stmt, BlockStatement):
    #                 if (
    #                     stmt.node.start_point[0] <= callee.start_point[0]
    #                     and stmt.node.end_point[0] >= callee.end_point[0]
    #                 ):
    #                     if stmt.node.start_point[0] == callee.start_point[0]:
    #                         stmt_calls = c_parser.query_all(
    #                             stmt.node, language.C.query_call
    #                         )
    #                         for stmt_call in stmt_calls:
    #                             if stmt_call.text == callee.text:
    #                                 return stmt
    #                     else:
    #                         return get_callee_stmt(stmt.statements, callee)
    #         return None
    #
    #     callees = {}
    #     nodes = c_parser.query_all(self.node, language.C.query_call)
    #     calls: dict[Node, str] = {
    #         node: node.text.decode() for node in nodes if node.text is not None
    #     }
    #     call_funcs: dict[Node, str] = {}
    #     for call_node in calls:
    #         func = call_node.child_by_field_name("function")
    #         assert func is not None
    #         if func.type == "identifier" and func.text is not None:
    #             call_funcs[call_node] = func.text.decode()
    #         else:
    #             for child in func.children:
    #                 if child.type == "identifier" and child.text is not None:
    #                     call_funcs[call_node] = child.text.decode()
    #                     break
    #     call_funcs_Func = {}
    #     for call in call_funcs.copy():
    #         accessible = False
    #         for func in self.accessible_functions:
    #             if func.name == call_funcs[call]:
    #                 accessible = True
    #                 call_funcs_Func[call_funcs[call]] = func
    #                 break
    #         if not accessible:
    #             call_funcs.pop(call)
    #
    #     for node in call_funcs:
    #         stmts = []
    #         callee_stmt = get_callee_stmt(self.statements, node)
    #         if callee_stmt is not None:
    #             stmts.append(callee_stmt)
    #         try:
    #             callees[call_funcs_Func[call_funcs[node]]].extend(stmts)
    #         except Exception:
    #             callees[call_funcs_Func[call_funcs[node]]] = stmts
    #
    #     return callees

    @cached_property
    def accessible_functions(self) -> list[Function]:
        funcs = []
        for file in self.file.imports:
            for function in file.functions:
                funcs.append(function)
        for func in self.file.functions:
            funcs.append(func)
        return funcs


class CPPFunction(Function, CBlockStatement):
    def __init__(self, node, file):
        super().__init__(node, file)


class PythonFunction(Function, PythonBlockStatement):
    def __init__(self, node, file):
        super().__init__(node, file)

    @property
    def name(self) -> str:
        name_node = self.node.child_by_field_name("name")
        assert name_node is not None
        assert name_node.text is not None
        return name_node.text.decode()

    @cached_property
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(self._statements_builder(self.body_node, self))

    def __find_next_nearest_stat(
        self, stat: Statement, jump: int = 0
    ) -> Statement | None:
        stat_type = stat.node.type
        if stat_type == "return_statement":
            return None

        if jump == -1:
            jump = 0x3F3F3F
        while (
            jump > 0
            and stat.parent is not None
            and isinstance(stat.parent, BlockStatement)
        ):
            stat = stat.parent
            jump -= 1

        parent_statements = stat.parent.statements
        index = parent_statements.index(stat)
        if (
            index < len(parent_statements) - 1
            and parent_statements[index + 1].node.type != "else_clause"
        ):
            return parent_statements[index + 1]
        else:
            if isinstance(stat.parent, Function):
                return None
            assert isinstance(stat.parent, BlockStatement)
            if stat.parent.node.type in language.PYTHON.loop_statements:
                return stat.parent
            else:
                return self.__find_next_nearest_stat(stat.parent)

    def _build_post_cfg(self, statements: list[Statement]):
        for i in range(len(statements)):
            cur_stat = statements[i]
            type = cur_stat.node.type
            next_stat = self.__find_next_nearest_stat(cur_stat)
            next_stat = [next_stat] if next_stat is not None else []

            if isinstance(cur_stat, BlockStatement):
                child_statements = cur_stat.statements
                self._build_post_cfg(child_statements)
                if len(child_statements) > 0:
                    match type:
                        case "if_statement":
                            else_clause = cur_stat.statements_by_type("else_clause")
                            if len(else_clause) == 0:
                                cur_stat._post_control_statements = [
                                    child_statements[0]
                                ] + next_stat
                            else:
                                if len(child_statements) == 1:
                                    cur_stat._post_control_statements = list(
                                        set([else_clause[0]] + next_stat)
                                    )
                                else:
                                    cur_stat._post_control_statements = list(
                                        set([child_statements[0], else_clause[0]])
                                    )
                        case "else_clause":
                            cur_stat._post_control_statements = [child_statements[0]]
                        case _:
                            cur_stat._post_control_statements = [
                                child_statements[0]
                            ] + next_stat
                else:
                    cur_stat._post_control_statements = next_stat
            elif isinstance(cur_stat, SimpleStatement):
                match type:
                    case "continue_statement":
                        # search for the nearest loop statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.PYTHON.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            cur_stat._post_control_statements.append(loop_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case "break_statement":
                        # search for the nearest loop or switch statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.PYTHON.loop_statements + ["match_statement"]
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            next_loop_stat = self.__find_next_nearest_stat(loop_stat)
                            cur_stat._post_control_statements = (
                                [next_loop_stat] if next_loop_stat else []
                            )
                        else:
                            cur_stat._post_control_statements = next_stat
                    case _:
                        cur_stat._post_control_statements = next_stat


class JavaScriptFunction(Function, JavaScriptBlockStatement):
    def __init__(self, node, file):
        super().__init__(node, file)

    @property
    def name(self) -> str:
        name_node = self.node.child_by_field_name("name")
        if name_node is None:
            return ""
        assert name_node.text is not None
        return name_node.text.decode()

    @cached_property
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(self._statements_builder(self.body_node, self))

    def __find_next_nearest_stat(
        self, stat: Statement, jump: int = 0
    ) -> Statement | None:
        stat_type = stat.node.type
        if stat_type == "return_statement":
            return None

        if jump == -1:
            jump = 0x3F3F3F
        while (
            jump > 0
            and stat.parent is not None
            and isinstance(stat.parent, BlockStatement)
        ):
            stat = stat.parent
            jump -= 1

        parent_statements = stat.parent.statements
        index = parent_statements.index(stat)
        if (
            index < len(parent_statements) - 1
            and parent_statements[index + 1].node.type != "else_clause"
        ):
            return parent_statements[index + 1]
        else:
            if isinstance(stat.parent, Function):
                return None
            assert isinstance(stat.parent, BlockStatement)
            if stat.parent.node.type in language.JAVASCRIPT.loop_statements:
                return stat.parent
            else:
                return self.__find_next_nearest_stat(stat.parent)

    def _build_post_cfg(self, statements: list[Statement]):
        for i in range(len(statements)):
            cur_stat = statements[i]
            type = cur_stat.node.type
            next_stat = self.__find_next_nearest_stat(cur_stat)
            next_stat = [next_stat] if next_stat is not None else []

            if isinstance(cur_stat, BlockStatement):
                child_statements = cur_stat.statements
                self._build_post_cfg(child_statements)
                if len(child_statements) > 0:
                    match type:
                        case "if_statement":
                            else_clause = cur_stat.statements_by_type("else_clause")
                            if len(else_clause) == 0:
                                cur_stat._post_control_statements = [
                                    child_statements[0]
                                ] + next_stat
                            else:
                                if len(child_statements) == 1:
                                    cur_stat._post_control_statements = list(
                                        set([else_clause[0]] + next_stat)
                                    )
                                else:
                                    cur_stat._post_control_statements = list(
                                        set([child_statements[0], else_clause[0]])
                                    )
                        case "else_clause":
                            cur_stat._post_control_statements = [child_statements[0]]
                        case _:
                            cur_stat._post_control_statements = [
                                child_statements[0]
                            ] + next_stat
                else:
                    cur_stat._post_control_statements = next_stat
            elif isinstance(cur_stat, SimpleStatement):
                match type:
                    case "continue_statement":
                        # search for the nearest loop statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.JAVASCRIPT.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            cur_stat._post_control_statements.append(loop_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case "break_statement":
                        # search for the nearest loop or switch statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.JAVASCRIPT.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            next_loop_stat = self.__find_next_nearest_stat(loop_stat)
                            cur_stat._post_control_statements = (
                                [next_loop_stat] if next_loop_stat else []
                            )
                        else:
                            cur_stat._post_control_statements = next_stat
                    case _:
                        cur_stat._post_control_statements = next_stat
