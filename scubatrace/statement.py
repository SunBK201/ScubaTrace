from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict, deque
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Generator

from tree_sitter import Node

from . import language
from .identifier import (
    CIdentifier,
    Identifier,
    JavaIdentifier,
    JavaScriptIdentifier,
    PythonIdentifier,
)
from .parser import cpp_parser, java_parser, javascript_parser, python_parser

if TYPE_CHECKING:
    from .file import File
    from .function import Function
    from .method import Method


class Statement:
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        self.node = node
        self.parent = parent
        self._pre_control_statements = []
        self._post_control_statements = []

    def __str__(self) -> str:
        return f"{self.signature}: {self.text}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Statement) and self.signature == value.signature

    def __hash__(self):
        return hash(self.signature)

    @cached_property
    @abstractmethod
    def identifiers(self) -> list[Identifier]: ...

    @cached_property
    @abstractmethod
    def variables(self) -> list[Identifier]: ...

    @property
    @abstractmethod
    def is_jump_statement(self) -> bool: ...

    @property
    def signature(self) -> str:
        return (
            self.parent.signature
            + "line"
            + str(self.start_line)
            + "-"
            + str(self.end_line)
            + "col"
            + str(self.start_column)
            + "-"
            + str(self.end_column)
        )

    @property
    def text(self) -> str:
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def dot_text(self) -> str:
        """
        escape the text ':' for dot
        """
        return '"' + self.text.replace('"', '\\"') + '"'

    @property
    def start_line(self) -> int:
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        return self.node.end_point[0] + 1

    @property
    def start_column(self) -> int:
        return self.node.start_point[1] + 1

    @property
    def end_column(self) -> int:
        return self.node.end_point[1] + 1

    @property
    def length(self):
        return self.end_line - self.start_line + 1

    @property
    def file(self) -> File:
        if "File" in self.parent.__class__.__name__:
            return self.parent  # type: ignore
        return self.parent.file  # type: ignore

    @property
    def function(self):
        cur = self
        while (
            "Function" not in cur.__class__.__name__
            and "Method" not in cur.__class__.__name__
        ):
            cur = cur.parent  # type: ignore
            if "File" in cur.__class__.__name__:
                return None
        return cur

    @property
    def post_controls(self) -> list[Statement]:
        func = self.function
        if func is None:
            return []
        assert (
            "Function" in func.__class__.__name__ or "Method" in func.__class__.__name__
        )
        if not func._is_build_cfg:  # type: ignore
            func.build_cfg()  # type: ignore
        return self._post_control_statements

    @post_controls.setter
    def post_controls(self, stats: list[Statement]):
        self._post_control_statements = stats

    @property
    def pre_controls(self) -> list[Statement]:
        func = self.function
        if func is None:
            return []
        assert (
            "Function" in func.__class__.__name__ or "Method" in func.__class__.__name__
        )
        if not func._is_build_cfg:  # type: ignore
            func.build_cfg()  # type: ignore
        return self._pre_control_statements

    @pre_controls.setter
    def pre_controls(self, stats: list[Statement]):
        self._pre_control_statements = stats

    @property
    def post_control_dependents(self) -> list[Statement]:
        if isinstance(self, SimpleStatement):
            return []
        assert isinstance(self, BlockStatement)
        dependents = []
        for child in self.statements:
            # post_control_dependent node is child node of self node in AST
            dependents.append(child)
            if child.is_jump_statement:
                break
        return dependents

    @property
    def pre_control_dependents(self) -> list[Statement]:
        parent = self.parent
        if (
            "Function" in parent.__class__.__name__
            or "Method" in parent.__class__.__name__
        ):
            return []
        if not isinstance(parent, Statement):
            return []
        for post in parent.post_control_dependents:
            if post == self:
                return [parent]
        return []

    @property
    def pre_data_dependents(self) -> dict[Identifier, list[Statement]]:
        dependents = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            if var.is_left_value:
                continue

            def is_data_dependents(stat: Statement) -> bool:
                if stat.signature == self.signature:
                    return False
                if isinstance(stat, BlockStatement):
                    stat_vars = stat.block_variables
                else:
                    stat_vars = stat.variables
                for stat_var in stat_vars:
                    if stat_var.text != var.text:
                        continue
                    if stat_var.is_left_value:
                        return True
                return False

            for pre in self.walk_backward(
                filter=is_data_dependents, stop_by=is_data_dependents
            ):
                dependents[var].append(pre)

        return dependents

    @property
    def post_data_dependents(self) -> dict[Identifier, list[Statement]]:
        dependents = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            if var.is_right_value:
                continue

            def is_data_dependents(stat: Statement) -> bool:
                if stat.signature == self.signature:
                    return False
                if isinstance(stat, BlockStatement):
                    stat_vars = stat.block_variables
                else:
                    stat_vars = stat.variables
                for stat_var in stat_vars:
                    if stat_var.text != var.text:
                        continue
                    return stat_var.is_right_value
                return False

            def is_right_value(stat: Statement) -> bool:
                if stat.signature == self.signature:
                    return False
                if isinstance(stat, BlockStatement):
                    stat_vars = stat.block_variables
                else:
                    stat_vars = stat.variables
                for stat_var in stat_vars:
                    if stat_var.text != var.text:
                        continue
                    return stat_var.is_left_value
                return False

            for post in self.walk_forward(
                filter=is_data_dependents, stop_by=is_right_value
            ):
                dependents[var].append(post)
        return dependents

    @property
    def references(self) -> dict[Identifier, list[Statement]]:
        refs = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        lsp = self.file.project.lsp
        self.file.lsp_preload()
        for var in variables:
            ref_stats: set[Statement] = set()
            ref_locs = lsp.request_references(
                self.file.relpath, var.start_line - 1, var.start_column - 1
            )
            def_locs = lsp.request_definition(
                self.file.relpath, var.start_line - 1, var.start_column - 1
            )
            ref_locs.extend(def_locs)  # add definition locations to references
            for loc in ref_locs:
                ref_path = loc["relativePath"]
                if ref_path is None:
                    continue
                if (ref_file := self.file.project.files[ref_path]) is None:
                    continue
                ref_line = loc["range"]["start"]["line"] + 1
                ref_func = ref_file.function_by_line(ref_line)
                if ref_func is None:
                    continue
                ref_stats.update(ref_func.statements_by_line(ref_line))
            refs[var] = sorted(ref_stats, key=lambda s: (s.start_line, s.start_column))
        return refs

    @property
    def definitions(self) -> dict[Identifier, list[Statement]]:
        defs = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        lsp = self.file.project.lsp
        self.file.lsp_preload()
        for var in variables:
            def_stats: set[Statement] = set()
            def_locs = lsp.request_definition(
                self.file.relpath, var.start_line - 1, var.start_column - 1
            )
            for loc in def_locs:
                def_path = loc["relativePath"]
                if def_path is None:
                    continue
                if (def_file := self.file.project.files[def_path]) is None:
                    continue
                def_line = loc["range"]["start"]["line"] + 1
                def_func = def_file.function_by_line(def_line)
                if def_func is None:
                    continue
                def_stats.update(def_func.statements_by_line(def_line))
            defs[var] = sorted(def_stats, key=lambda s: (s.start_line, s.start_column))
        return defs

    @cached_property
    def is_taint_from_entry(self) -> bool:
        refs: dict[Identifier, list[Statement]] = self.references
        backword_refs: dict[Identifier, list[Statement]] = defaultdict(list)
        for var, statements in refs.items():
            for stat in statements:
                if stat.start_line < self.start_line:
                    backword_refs[var].append(stat)
        if len(backword_refs) == 0:
            return False

        for var, statements in backword_refs.items():
            for stat in statements:
                if (
                    "Function" in stat.__class__.__name__
                    or "Method" in stat.__class__.__name__
                ):
                    return True
                for stat_var in stat.variables:
                    if stat_var.text != var.text:
                        continue
                    if stat_var.is_left_value and stat.is_taint_from_entry:
                        return True
        return False

    def walk_backward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
        depth: int = -1,
        base: str = "control",
    ) -> Generator[Statement, None, None]:
        depth = 2048 if depth == -1 else depth
        dq: deque[Statement] = deque([self])
        visited: set[Statement] = set([self])
        while len(dq) > 0 and depth >= 0:
            size = len(dq)
            for _ in range(size):
                cur_stat = dq.pop()
                if filter is not None and filter(cur_stat) or filter is None:
                    yield cur_stat
                if stop_by is not None and stop_by(cur_stat):
                    continue
                match base:
                    case "control":
                        nexts = cur_stat.pre_controls
                    case "data_dependent":
                        nexts = []
                        for stats in cur_stat.pre_data_dependents.values():
                            nexts.extend(stats)
                    case "control_dependent":
                        nexts = cur_stat.pre_control_dependents
                    case _:
                        nexts = cur_stat.pre_controls
                for pre in nexts:
                    if pre in visited:
                        continue
                    visited.add(pre)
                    dq.appendleft(pre)
            depth -= 1

    def walk_forward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
        depth: int = -1,
        base: str = "control",
    ) -> Generator[Statement, None, None]:
        depth = 2048 if depth == -1 else depth
        dq: deque[Statement] = deque([self])
        visited: set[Statement] = set([self])
        while len(dq) > 0 and depth >= 0:
            size = len(dq)
            for _ in range(size):
                cur_stat = dq.pop()
                if filter is not None and filter(cur_stat) or filter is None:
                    yield cur_stat
                if stop_by is not None and stop_by(cur_stat):
                    continue
                match base:
                    case "control":
                        nexts = cur_stat.post_controls
                    case "data_dependent":
                        nexts = []
                        for stats in cur_stat.post_data_dependents.values():
                            nexts.extend(stats)
                    case "control_dependent":
                        nexts = cur_stat.post_control_dependents
                    case _:
                        nexts = cur_stat.post_controls
                for post in nexts:
                    if post in visited:
                        continue
                    visited.add(post)
                    dq.appendleft(post)
            depth -= 1


class SimpleStatement(Statement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)


class BlockStatement(Statement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    def __getitem__(self, index: int) -> Statement:
        return self.statements[index]

    def __traverse_statements(self):
        stack = []
        for stat in self.statements:
            stack.append(stat)
            while stack:
                cur_stat = stack.pop()
                yield cur_stat
                if isinstance(cur_stat, BlockStatement):
                    stack.extend(reversed(cur_stat.statements))

    @property
    def dot_text(self) -> str:
        """
        return only the first line of the text
        """
        return '"' + self.text.split("\n")[0].replace('"', '\\"') + '..."'

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]: ...

    @cached_property
    @abstractmethod
    def block_identifiers(self) -> list[Identifier]: ...

    @cached_property
    @abstractmethod
    def block_variables(self) -> list[Identifier]: ...

    def statements_by_line(self, line: int) -> list[Statement]:
        targets = []
        for stat in self.statements:
            if stat.start_line <= line <= stat.end_line:
                if isinstance(stat, BlockStatement):
                    if stat.__is_line_in_block(line):
                        targets.append(stat)
                    targets.extend(stat.statements_by_line(line))
                    if len(targets) == 0:
                        targets.append(stat)
                elif isinstance(stat, SimpleStatement):
                    targets.append(stat)
        if len(targets) == 0:
            if self.start_line <= line <= self.end_line:
                targets.append(self)
        return targets

    def statements_by_type(self, type: str, recursive: bool = False) -> list[Statement]:
        if recursive:
            return [s for s in self.__traverse_statements() if s.node.type == type]
        else:
            return [s for s in self.statements if s.node.type == type]

    def __is_line_in_block(self, line: int) -> bool:
        # TODO
        return self.start_line == line


class CSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @property
    def is_jump_statement(self) -> bool:
        return self.node.type in language.C.jump_statements

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = cpp_parser.query_all(self.node, language.C.query_identifier)
        identifiers = [
            CIdentifier(node, self) for node in nodes if node.text is not None
        ]
        return list(identifiers)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
            ]:
                continue
            variables.append(identifier)
        return variables


class CBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = cpp_parser.query_all(self.node, language.C.query_identifier)
        identifiers = set(
            [CIdentifier(node, self) for node in nodes if node.text is not None]
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        identifiers -= identifiers_in_children  # remove identifiers in children base the hash of Identifier
        identifiers |= identifiers_in_children
        return list(identifiers)

    @cached_property
    def block_identifiers(self) -> list[Identifier]:
        nodes = cpp_parser.query_all(self.node, language.C.query_identifier)
        identifiers = set(
            CIdentifier(node, self) for node in nodes if node.text is not None
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        return list(identifiers - identifiers_in_children)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
            ]:
                continue
            variables.append(identifier)
        return variables

    @cached_property
    def block_variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.block_identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
            ]:
                continue
            variables.append(identifier)
        return variables

    @staticmethod
    def is_block_statement(node: Node) -> bool:
        return node.type in language.C.block_statements

    @staticmethod
    def is_simple_statement(node: Node) -> bool:
        if node.parent is None:
            return False
        else:
            if node.parent.type in language.C.simple_statements:
                return False
            elif (
                node.parent.type in language.C.control_statements
                and node.parent.child_by_field_name("body") != node
                and node.parent.child_by_field_name("consequence") != node
            ):
                return False
            else:
                return node.type in language.C.simple_statements

    @property
    def is_jump_statement(self) -> bool:
        if self.node.type in language.C.loop_statements:
            return False
        for child in self.statements:
            if child.is_jump_statement:
                return True
        return False

    def _statements_builder(
        self,
        node: Node,
        parent: BlockStatement | Function | File,
    ) -> Generator[Statement, None, None]:
        cursor = node.walk()
        if cursor.node is not None:
            if not cursor.goto_first_child():
                yield from ()
        while True:
            assert cursor.node is not None
            if self.is_simple_statement(cursor.node):
                yield CSimpleStatement(cursor.node, parent)
            elif self.is_block_statement(cursor.node):
                yield CBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if consequence_node is not None and consequence_node.type in [
                    "compound_statement"
                ]:
                    stats.extend(list(self._statements_builder(consequence_node, self)))
                elif consequence_node is not None:
                    stats.extend([CSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:
                    stats.extend([CBlockStatement(else_clause_node, self)])
            case "else_clause":
                compound_node = None
                for child in self.node.children:
                    if child.type == "compound_statement":
                        compound_node = child
                if compound_node is not None:
                    stats.extend(list(self._statements_builder(compound_node, self)))
                else:
                    stats.extend(list(self._statements_builder(self.node, self)))
            case "for_range_loop":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "while_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "do_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([CSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([CBlockStatement(body_node, self)])
            case "switch_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["compound_statement"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    stats.extend([CSimpleStatement(body_node, self)])
            case "case_statement":
                get_compound = False
                for child in self.node.children:
                    if child.type in ["compound_statement"]:
                        stats.extend(list(self._statements_builder(child, self)))
                        get_compound = True
                if not get_compound:
                    stats.extend(list(self._statements_builder(self.node, self)))
            case _:
                stats.extend(list(self._statements_builder(self.node, self)))
        return stats


class JavaSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Method):
        super().__init__(node, parent)

    @property
    def is_jump_statement(self) -> bool:
        return self.node.type in language.JAVA.jump_statements

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = java_parser.query_all(self.node, language.JAVA.query_identifier)
        identifiers = [
            JavaIdentifier(node, self) for node in nodes if node.text is not None
        ]
        return list(identifiers)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "method_invocation",
                "method_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables


class JavaBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: BlockStatement | Method):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = java_parser.query_all(self.node, language.JAVA.query_identifier)
        identifiers = set(
            [JavaIdentifier(node, self) for node in nodes if node.text is not None]
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        identifiers -= identifiers_in_children  # remove identifiers in children base the hash of Identifier
        identifiers |= identifiers_in_children
        return list(identifiers)

    @cached_property
    def block_identifiers(self) -> list[Identifier]:
        nodes = java_parser.query_all(self.node, language.JAVA.query_identifier)
        identifiers = set(
            JavaIdentifier(node, self) for node in nodes if node.text is not None
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        return list(identifiers - identifiers_in_children)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "method_invocation",
                "method_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @cached_property
    def block_variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.block_identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "method_invocation",
                "method_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @staticmethod
    def is_block_statement(node: Node) -> bool:
        return node.type in language.JAVA.block_statements

    @staticmethod
    def is_simple_statement(node: Node) -> bool:
        if node.parent is None:
            return False
        else:
            if node.parent.type in language.JAVA.simple_statements:
                return False
            elif (
                node.parent.type in language.JAVA.control_statements
                and node.parent.child_by_field_name("body") != node
                and node.parent.child_by_field_name("consequence") != node
            ):
                return False
            else:
                return node.type in language.JAVA.simple_statements

    @property
    def is_jump_statement(self) -> bool:
        if self.node.type in language.JAVA.loop_statements:
            return False
        for child in self.statements:
            if child.is_jump_statement:
                return True
        return False

    def _statements_builder(
        self,
        node: Node,
        parent: BlockStatement | Method,
    ) -> Generator[Statement, None, None]:
        cursor = node.walk()
        if cursor.node is not None:
            if not cursor.goto_first_child():
                yield from ()
        while True:
            assert cursor.node is not None
            if self.is_simple_statement(cursor.node):
                yield JavaSimpleStatement(cursor.node, parent)
            elif self.is_block_statement(cursor.node):
                yield JavaBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if consequence_node is not None and consequence_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(consequence_node, self)))
                elif consequence_node is not None:
                    stats.extend([JavaSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:
                    stats.extend([JavaBlockStatement(else_clause_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaBlockStatement(body_node, self)])
            case "enhanced_for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaBlockStatement(body_node, self)])
            case "while_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaBlockStatement(body_node, self)])
            case "do_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaBlockStatement(body_node, self)])
            case "switch_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["switch_block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    stats.extend([JavaSimpleStatement(body_node, self)])
            case "switch_block_statement_group":
                get_compound = False
                for child in self.node.children:
                    if child.type in ["block"]:
                        stats.extend(list(self._statements_builder(child, self)))
                        get_compound = True
                if not get_compound:
                    stats.extend(list(self._statements_builder(self.node, self)))
            case _:
                stats.extend(list(self._statements_builder(self.node, self)))
        return stats


class PythonSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = python_parser.query_all(self.node, language.PYTHON.query_identifier)
        identifiers = [
            PythonIdentifier(node, self) for node in nodes if node.text is not None
        ]
        return list(identifiers)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call",
                "function_definition",
            ]:
                continue
            variables.append(identifier)
        return variables


class PythonBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = python_parser.query_all(self.node, language.PYTHON.query_identifier)
        identifiers = set(
            [PythonIdentifier(node, self) for node in nodes if node.text is not None]
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        identifiers -= identifiers_in_children  # remove identifiers in children base the hash of Identifier
        identifiers |= identifiers_in_children
        return list(identifiers)

    @cached_property
    def block_identifiers(self) -> list[Identifier]:
        nodes = python_parser.query_all(self.node, language.PYTHON.query_identifier)
        identifiers = set(
            PythonIdentifier(node, self) for node in nodes if node.text is not None
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        return list(identifiers - identifiers_in_children)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call",
                "function_definition",
            ]:
                continue
            variables.append(identifier)
        return variables

    @cached_property
    def block_variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.block_identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call",
                "function_definition",
            ]:
                continue
            variables.append(identifier)
        return variables

    @staticmethod
    def is_block_statement(node: Node) -> bool:
        return node.type in language.PYTHON.block_statements

    @staticmethod
    def is_simple_statement(node: Node) -> bool:
        if node.parent is None:
            return False
        else:
            if node.parent.type in language.PYTHON.simple_statements:
                return False
            elif (
                node.parent.type in language.PYTHON.control_statements
                and node.parent.child_by_field_name("body") != node
                and node.parent.child_by_field_name("consequence") != node
            ):
                return False
            else:
                return node.type in language.PYTHON.simple_statements

    @property
    def is_jump_statement(self) -> bool:
        if self.node.type in language.PYTHON.loop_statements:
            return False
        for child in self.statements:
            if child.is_jump_statement:
                return True
        return False

    def _statements_builder(
        self,
        node: Node,
        parent: BlockStatement | Method,
    ) -> Generator[Statement, None, None]:
        cursor = node.walk()
        if cursor.node is not None:
            if not cursor.goto_first_child():
                yield from ()
        while True:
            assert cursor.node is not None
            if self.is_simple_statement(cursor.node):
                yield PythonSimpleStatement(cursor.node, parent)
            elif self.is_block_statement(cursor.node):
                yield PythonBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if consequence_node is not None and consequence_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(consequence_node, self)))
                elif consequence_node is not None:
                    stats.extend([PythonSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:
                    stats.extend([PythonBlockStatement(else_clause_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([PythonSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([PythonBlockStatement(body_node, self)])
            case "while_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([PythonSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([PythonBlockStatement(body_node, self)])
            case "match_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    stats.extend([PythonSimpleStatement(body_node, self)])
            case _:
                stats.extend(list(self._statements_builder(self.node, self)))
        return stats


class JavaScriptSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = javascript_parser.query_all(
            self.node, language.JAVASCRIPT.query_identifier
        )
        identifiers = [
            JavaScriptIdentifier(node, self) for node in nodes if node.text is not None
        ]
        return list(identifiers)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables


class JavaScriptBlockStatement(BlockStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = javascript_parser.query_all(
            self.node, language.JAVASCRIPT.query_identifier
        )
        identifiers = set(
            [
                JavaScriptIdentifier(node, self)
                for node in nodes
                if node.text is not None
            ]
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        identifiers -= identifiers_in_children  # remove identifiers in children base the hash of Identifier
        identifiers |= identifiers_in_children
        return list(identifiers)

    @cached_property
    def block_identifiers(self) -> list[Identifier]:
        nodes = javascript_parser.query_all(
            self.node, language.JAVASCRIPT.query_identifier
        )
        identifiers = set(
            JavaScriptIdentifier(node, self) for node in nodes if node.text is not None
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        return list(identifiers - identifiers_in_children)

    @cached_property
    def variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @cached_property
    def block_variables(self) -> list[Identifier]:
        variables = []
        for identifier in self.block_identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @staticmethod
    def is_block_statement(node: Node) -> bool:
        return node.type in language.JAVASCRIPT.block_statements

    @staticmethod
    def is_simple_statement(node: Node) -> bool:
        if node.parent is None:
            return False
        else:
            if node.parent.type in language.JAVASCRIPT.simple_statements:
                return False
            elif (
                node.parent.type in language.JAVASCRIPT.control_statements
                and node.parent.child_by_field_name("body") != node
                and node.parent.child_by_field_name("consequence") != node
            ):
                return False
            else:
                return node.type in language.JAVASCRIPT.simple_statements

    @property
    def is_jump_statement(self) -> bool:
        if self.node.type in language.JAVASCRIPT.loop_statements:
            return False
        for child in self.statements:
            if child.is_jump_statement:
                return True
        return False

    def _statements_builder(
        self,
        node: Node,
        parent: BlockStatement | Function | File,
    ) -> Generator[Statement, None, None]:
        cursor = node.walk()
        if cursor.node is not None:
            if not cursor.goto_first_child():
                yield from ()
        while True:
            assert cursor.node is not None
            if self.is_simple_statement(cursor.node):
                yield JavaScriptSimpleStatement(cursor.node, parent)
            elif self.is_block_statement(cursor.node):
                yield JavaScriptBlockStatement(cursor.node, parent)

            if not cursor.goto_next_sibling():
                break

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        type = self.node.type
        match type:
            case "if_statement":
                consequence_node = self.node.child_by_field_name("consequence")
                if consequence_node is not None and consequence_node.type in [
                    "statement_block"
                ]:
                    stats.extend(list(self._statements_builder(consequence_node, self)))
                elif consequence_node is not None:
                    stats.extend([JavaScriptSimpleStatement(consequence_node, self)])
                else_clause_node = self.node.child_by_field_name("alternative")
                if else_clause_node is not None:
                    stats.extend([JavaScriptBlockStatement(else_clause_node, self)])
            case "for_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["statement_block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaScriptSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaScriptBlockStatement(body_node, self)])
            case "while_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["statement_block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaScriptSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaScriptBlockStatement(body_node, self)])
            case "do_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["statement_block"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    if self.is_simple_statement(body_node):
                        stats.extend([JavaScriptSimpleStatement(body_node, self)])
                    elif self.is_block_statement(body_node):
                        stats.extend([JavaScriptBlockStatement(body_node, self)])
            case "switch_statement":
                body_node = self.node.child_by_field_name("body")
                if body_node is not None and body_node.type in ["switch_body"]:
                    stats.extend(list(self._statements_builder(body_node, self)))
                elif body_node is not None:
                    stats.extend([JavaScriptSimpleStatement(body_node, self)])
            case "switch_case":
                for child in self.node.children:
                    stats.extend(list(self._statements_builder(child, self)))
            case _:
                stats.extend(list(self._statements_builder(self.node, self)))
        return stats
