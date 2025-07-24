from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict, deque
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Generator

from tree_sitter import Node

from .identifier import Identifier
from .language import Language

if TYPE_CHECKING:
    from .file import File
    from .function import Function


class Statement:
    """
    A statement in the source code.
    """

    node: Node
    """ The tree-sitter node representing this statement. """

    parent: BlockStatement | Function | File
    """ The parent block or function or file this statement belongs to. """

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

    @property
    @abstractmethod
    def is_jump_statement(self) -> bool:
        """
        Checks if the statement is a jump statement (e.g., break, continue, return).
        """
        ...

    @property
    def language(self) -> type[Language]:
        """
        The language of the file this statement belongs to.
        """
        return self.file.language

    @property
    def lsp(self):
        return self.file.lsp

    @cached_property
    def identifiers(self) -> list[Identifier]:
        """
        Identifiers in the statement.

        This includes variables, function names, and other identifiers.
        """
        parser = self.file.parser
        language = self.language
        nodes = parser.query_all(self.node, language.query_identifier)
        identifiers = set(
            [Identifier(node, self) for node in nodes if node.text is not None]
        )
        if isinstance(self, BlockStatement):
            identifiers_in_children = set()
            for stat in self.statements:
                identifiers_in_children.update(stat.identifiers)
            identifiers -= identifiers_in_children  # remove identifiers in children base the hash of Identifier
            identifiers |= identifiers_in_children
        return sorted(identifiers, key=lambda x: (x.start_line, x.start_column))

    @cached_property
    def variables(self) -> list[Identifier]:
        """
        Variables in the statement.
        """
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
                "method_invocation",
                "method_declaration",
                "call",
                "function_definition",
                "call_expression",
                "function_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @property
    def right_values(self) -> list[Identifier]:
        """
        Variables that are right values in the statement.

        Right values are variables that are used in the statement but not modified or assigned.
        """
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        return [id for id in variables if id.is_right_value]

    @property
    def left_values(self) -> list[Identifier]:
        """
        Variables that are left values in the statement.

        Left values are variables that are modified or assigned in the statement.
        """
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        return [id for id in variables if id.is_left_value]

    @property
    def signature(self) -> str:
        """
        A unique signature for the statement.
        """
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
        """
        The text of the statement.
        """
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def dot_text(self) -> str:
        return '"' + self.text.replace('"', '\\"') + '"'

    @property
    def start_line(self) -> int:
        """
        The start line of the statement.
        """
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        """
        The end line of the statement.
        """
        return self.node.end_point[0] + 1

    @property
    def start_column(self) -> int:
        """
        The start column of the statement.
        """
        return self.node.start_point[1] + 1

    @property
    def end_column(self) -> int:
        """
        The end column of the statement.
        """
        return self.node.end_point[1] + 1

    @property
    def length(self):
        """
        The length of the statement in lines."""
        return self.end_line - self.start_line + 1

    @property
    def file(self) -> File:
        """
        The file this statement belongs to.
        """
        from .file import File

        if isinstance(self.parent, File):
            return self.parent
        return self.parent.file

    @property
    def function(self) -> Function | None:
        """
        The function this statement belongs to, if any.

        If the statement is not part of a function, returns None.
        """
        from .file import File
        from .function import Function

        cur = self

        while not isinstance(cur, Function):
            cur = cur.parent
            if isinstance(cur, File):
                return None
        return cur

    @property
    def post_controls(self) -> list[Statement]:
        """
        Post-control statements of the statement.

        These are statements that are executed after this statement in the control flow.
        """
        func = self.function
        if func is None:
            return []
        if not func._is_build_cfg:
            func.build_cfg()
        return self._post_control_statements

    @post_controls.setter
    def post_controls(self, stats: list[Statement]):
        self._post_control_statements = stats

    @property
    def pre_controls(self) -> list[Statement]:
        """
        Pre-control statements of the statement.

        These are statements that are executed before this statement in the control flow.
        """
        func = self.function
        if func is None:
            return []
        if not func._is_build_cfg:
            func.build_cfg()
        return self._pre_control_statements

    @pre_controls.setter
    def pre_controls(self, stats: list[Statement]):
        self._pre_control_statements = stats

    @property
    def post_control_dependents(self) -> list[Statement]:
        """
        Statements that are dependent on this statement in the control flow.
        """
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
        """
        Statements that are dependent on this statement in the control flow before it.
        """
        parent = self.parent
        from .function import Function

        if isinstance(parent, Function):
            return []
        if not isinstance(parent, Statement):
            return []
        for post in parent.post_control_dependents:
            if post == self:
                return [parent]
        return []

    @property
    def pre_data_dependents(self) -> dict[Identifier, list[Statement]]:
        """
        Data-dependent statements that are executed before this statement.
        """
        dependents = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            var_deps_stats = set(
                var_dep.statement for var_dep in var.pre_data_dependents
            )
            dependents[var] = sorted(var_deps_stats, key=lambda x: x.start_line)
        return dependents

    @property
    def post_data_dependents(self) -> dict[Identifier, list[Statement]]:
        """
        Data-dependent statements that are executed after this statement.
        """
        dependents = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            var_deps_stats = set(
                var_dep.statement for var_dep in var.post_data_dependents
            )
            dependents[var] = sorted(var_deps_stats, key=lambda x: x.start_line)
        return dependents

    @property
    def references(self) -> dict[Identifier, list[Statement]]:
        """
        References to variables in the statement.

        Includes variables that are in the whole project.
        """
        refs = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            ref_vars = var.references
            ref_vars_stats = set(ref_var.statement for ref_var in ref_vars)
            refs[var] = sorted(ref_vars_stats, key=lambda x: x.start_line)
        return refs

    @property
    def definitions(self) -> dict[Identifier, list[Statement]]:
        """
        Definitions of variables in the statement.

        Includes variables that are defined in the whole project.
        """
        defs = defaultdict(list)
        if isinstance(self, BlockStatement):
            variables = self.block_variables
        else:
            variables = self.variables
        for var in variables:
            def_vars = var.definitions
            def_vars_stats = set(def_var.statement for def_var in def_vars)
            defs[var] = sorted(def_vars_stats, key=lambda x: x.start_line)
        return defs

    @cached_property
    def is_taint_from_entry(self) -> bool:
        """
        Checks if the variables of the statement are tainted from the parameters of the function.
        """
        refs: dict[Identifier, list[Statement]] = self.references
        backword_refs: dict[Identifier, list[Statement]] = defaultdict(list)
        for var, statements in refs.items():
            for stat in statements:
                if stat.start_line < self.start_line:
                    backword_refs[var].append(stat)
        if len(backword_refs) == 0:
            return False

        from .function import Function

        for var, statements in backword_refs.items():
            for stat in statements:
                if isinstance(stat, Function):
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
        """
        Walks backward through the control flow graph of the statement.

        Args:
            filter (Callable[[Statement], bool] | None): A filter function to apply to each statement.
                If the filter returns True, the statement is yielded.
            stop_by (Callable[[Statement], bool] | None): A function to stop the walking when it returns True.
            depth (int): The maximum depth to walk backward. Default is -1, which means no limit.
            base (str): The base type of the walk.
                Can be "control", "data_dependent", or "control_dependent".

        Yields:
            Statement: The statements that match the filter or all statements if no filter is provided.
        """
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
        """
        Walks forward through the control flow graph of the statement.

        Args:
            filter (Callable[[Statement], bool] | None): A filter function to apply to each statement.
                If the filter returns True, the statement is yielded.
            stop_by (Callable[[Statement], bool] | None): A function to stop the walking when it returns True.
            depth (int): The maximum depth to walk forward. Default is -1, which means no limit.
            base (str): The base type of the walk.
                Can be "control", "data_dependent", or "control_dependent".

        Yields:
            Statement: The statements that match the filter or all statements if no filter is provided.
        """
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
    @property
    def is_jump_statement(self) -> bool:
        language = self.language
        return self.node.type in language.jump_statements


class BlockStatement(Statement):
    def __getitem__(self, index: int) -> Statement:
        return self.statements[index]

    @property
    def dot_text(self) -> str:
        return '"' + self.text.split("\n")[0].replace('"', '\\"') + '..."'

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]:
        """
        Sub-statements of the block.
        """
        ...

    @cached_property
    def block_identifiers(self) -> list[Identifier]:
        """
        Identifiers declared directly in the block.

        Only includes identifiers that are declared in this block and excludes those found in sub-statements.
        """
        parser = self.file.parser
        language = self.language
        nodes = parser.query_all(self.node, language.query_identifier)
        identifiers = set(
            Identifier(node, self) for node in nodes if node.text is not None
        )
        identifiers_in_children = set()
        for stat in self.statements:
            identifiers_in_children.update(stat.identifiers)
        return list(identifiers - identifiers_in_children)

    @cached_property
    def block_variables(self) -> list[Identifier]:
        """
        Variables declared directly in the block.

        Only includes variables that are declared in this block and excludes those found in sub-statements.
        """
        variables = []
        for identifier in self.block_identifiers:
            node = identifier.node
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
                "method_invocation",
                "method_declaration",
                "call",
                "function_definition",
                "call_expression",
                "function_declaration",
            ]:
                continue
            variables.append(identifier)
        return variables

    @property
    def is_jump_statement(self) -> bool:
        language = self.language
        if self.node.type in language.loop_statements:
            return False
        for child in self.statements:
            if child.is_jump_statement:
                return True
        return False

    def __traverse_statements(self):
        stack = []
        for stat in self.statements:
            stack.append(stat)
            while stack:
                cur_stat = stack.pop()
                yield cur_stat
                if isinstance(cur_stat, BlockStatement):
                    stack.extend(reversed(cur_stat.statements))

    def statements_by_line(self, line: int) -> list[Statement]:
        """
        Returns the statements that are located on the specified line number.

        Args:
            line (int): The line number to check.

        Returns:
            list[Statement]: A list of statements that are located on the specified line.
        """
        targets = []
        for stat in self.statements:
            if stat.start_line <= line <= stat.end_line:
                if isinstance(stat, BlockStatement):
                    sub_targets = stat.statements_by_line(line)
                    targets.extend(sub_targets)
                    if len(sub_targets) == 0:
                        targets.append(stat)
                elif isinstance(stat, SimpleStatement):
                    targets.append(stat)
        if len(targets) == 0:
            if self.start_line <= line <= self.end_line:
                targets.append(self)
        return targets

    def statements_by_type(self, type: str, recursive: bool = False) -> list[Statement]:
        """
        Returns the statements that are of the specified type.

        Args:
            type (str): The tree-sitter ast type of the statements to return.
            recursive (bool): If True, recursively search in sub-statements.

        Returns:
            list[Statement]: A list of statements that match the specified type.
        """
        if recursive:
            return [s for s in self.__traverse_statements() if s.node.type == type]
        else:
            return [s for s in self.statements if s.node.type == type]

    def statement_by_field_name(self, field_name: str) -> Statement | None:
        """
        Returns the statement that contains the specified tree-sitter ast field name.

        Args:
            field_name (str): The tree-sitter ast field name to search for.

        Returns:
            Optional[Statement]: The statement that contains the specified field name, or None if not found.
        """
        field_node = self.node.child_by_field_name(field_name)
        if field_node is None:
            return None
        for stat in self.statements:
            if stat.node.start_byte == field_node.start_byte:
                return stat
        return None
