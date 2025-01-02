from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict, deque
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Generator

from tree_sitter import Node

from . import language
from .identifier import CIdentifier, Identifier
from .parser import c_parser

if TYPE_CHECKING:
    from .file import File
    from .function import Function


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
        while "Function" not in cur.__class__.__name__:
            cur = cur.parent  # type: ignore
            if "File" in cur.__class__.__name__:
                return None
        return cur

    @property
    def post_controls(self) -> list[Statement]:
        func = self.function
        if func is None:
            return []
        assert "Function" in func.__class__.__name__
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
        assert "Function" in func.__class__.__name__
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
                    return True
                return False

            for post in self.walk_forward(
                filter=is_data_dependents, stop_by=is_data_dependents
            ):
                dependents[var].append(post)
        return dependents

    def walk_backward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
    ) -> Generator[Statement, None, None]:
        dq: deque[Statement] = deque([self])
        visited: set[Statement] = set([self])
        while len(dq) > 0:
            cur_stat = dq.pop()
            if filter is not None and filter(cur_stat):
                yield cur_stat
            if stop_by is not None and stop_by(cur_stat):
                continue
            for pre in cur_stat.pre_controls:
                if pre in visited:
                    continue
                visited.add(pre)
                dq.appendleft(pre)

    def walk_forward(
        self,
        filter: Callable[[Statement], bool] | None = None,
        stop_by: Callable[[Statement], bool] | None = None,
    ) -> Generator[Statement, None, None]:
        dq: deque[Statement] = deque([self])
        visited: set[Statement] = set([self])
        while len(dq) > 0:
            cur_stat = dq.pop()
            if filter is not None and filter(cur_stat):
                yield cur_stat
            if stop_by is not None and stop_by(cur_stat):
                continue
            for post in cur_stat.post_controls:
                if post in visited:
                    continue
                visited.add(post)
                dq.appendleft(post)


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
    def statements(self) -> list[Statement]: ...

    @cached_property
    @abstractmethod
    def block_identifiers(self) -> list[Identifier]: ...

    @cached_property
    @abstractmethod
    def block_variables(self) -> list[Identifier]: ...

    def statements_by_type(self, type: str, recursive: bool = False) -> list[Statement]:
        if recursive:
            return [s for s in self.__traverse_statements() if s.node.type == type]
        else:
            return [s for s in self.statements if s.node.type == type]


class CSimpleStatement(SimpleStatement):
    def __init__(self, node: Node, parent: BlockStatement | Function | File):
        super().__init__(node, parent)

    @property
    def is_jump_statement(self) -> bool:
        return self.node.type in language.C.jump_statements

    @cached_property
    def identifiers(self) -> list[Identifier]:
        nodes = c_parser.query_all(self.node, language.C.query_identifier)
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
        nodes = c_parser.query_all(self.node, language.C.query_identifier)
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
        nodes = c_parser.query_all(self.node, language.C.query_identifier)
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
