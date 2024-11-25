from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from . import language
from .parser import c_parser
from .statement import (
    CBlockStatement,
    CSimpleStatement,
    CStatement,
    Statement,
)

if TYPE_CHECKING:
    from .file import File


class Function:
    """
    Represents a function in the source code with various properties and methods to access its details.

    Attributes:
        node (Node): The AST node representing the function.
        file (File): The file in which the function is defined.
    """

    def __init__(self, node: Node, file: File):
        """
        Initializes a new instance of the class.

        Args:
            node (Node): The node associated with this instance.
            file (File): The file associated with this instance.
        """
        self.node = node
        self.file = file

    def __str__(self) -> str:
        return self.signature

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
    def text(self) -> str:
        """
        Returns the text content of the node.

        Raises:
            ValueError: If the node's text is None.

        Returns:
            str: The decoded text content of the node.
        """
        if self.node.text is None:
            raise ValueError("Node text is None")
        return self.node.text.decode()

    @property
    def start_line(self) -> int:
        """
        Returns the starting line number of the node.

        The line number is determined by the node's start point and is incremented by 1
        to convert from a zero-based index to a one-based index.

        Returns:
            int: The starting line number of the node.
        """
        return self.node.start_point[0] + 1

    @property
    def end_line(self) -> int:
        """
        Returns the ending line number of the node.

        The line number is derived from the node's end_point attribute and is
        incremented by 1 to convert from a zero-based index to a one-based index.

        Returns:
            int: The ending line number of the node.
        """
        return self.node.end_point[0] + 1

    @property
    def length(self):
        """
        Calculate the length of the range.

        Returns:
            int: The length of the range, calculated as the difference between
            end_line and start_line, plus one.
        """
        return self.end_line - self.start_line + 1

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
    def statements(self) -> list[Statement]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def identifiers(self) -> dict[Node, str]: ...

    @property
    @abstractmethod
    def variables(self) -> dict[Node, str]: ...

    @cached_property
    @abstractmethod
    def accessible_functions(self) -> list[Function]: ...

    @cached_property
    @abstractmethod
    def calls(self) -> list[Statement]: ...

    @cached_property
    @abstractmethod
    def callees(self) -> dict[Function, list[Statement]]: ...

    @cached_property
    @abstractmethod
    def callers(self) -> dict[Function, list[Statement]]: ...


class CFunction(Function):
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
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(CStatement.generater(self.body_node, self))

    @property
    def identifiers(self) -> dict[Node, str]:
        nodes = c_parser.query_all(self.node, language.C.query_identifier)
        identifiers = {
            node: node.text.decode() for node in nodes if node.text is not None
        }
        return identifiers

    @property
    def variables(self) -> dict[Node, str]:
        variables = self.identifiers
        for node in self.identifiers:
            if node.parent is not None and node.parent.type in [
                "call_expression",
                "function_declarator",
            ]:
                variables.pop(node)
        return variables

    @cached_property
    def calls(self) -> list[Statement]:
        nodes = c_parser.query_all(self.node, language.C.query_call)
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

    @cached_property
    def callers(self) -> dict[Function, list[Statement]]:
        callers = {}
        for file in self.file.project.files:
            for func in self.file.project.files[file].functions:
                if self in func.callees:
                    for stmt in func.callees[self]:
                        try:
                            callers[func].append(stmt)
                        except Exception:
                            callers[func] = [stmt]
        return callers

    @cached_property
    def callees(self) -> dict[Function, list[Statement]]:
        callees = {}
        nodes = c_parser.query_all(self.node, language.C.query_call)
        calls: dict[Node, str] = {
            node: node.text.decode() for node in nodes if node.text is not None
        }
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
            stmts = []
            for stmt in self.statements:
                if (
                    stmt.node.start_point[0] == node.start_point[0]
                    and stmt.node.text == node.text
                ):
                    stmts.append(stmt)
                    break
            callees[call_funcs[node]] = stmts

        return callees

    @cached_property
    def accessible_functions(self) -> list[Function]:
        funcs = []
        for file in self.file.imports:
            for function in file.functions:
                funcs.append(function)
        return funcs
