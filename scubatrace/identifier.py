from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from tree_sitter import Node

from .parser import cpp_parser, java_parser, javascript_parser, python_parser

if TYPE_CHECKING:
    from .file import File
    from .statement import Statement


class Identifier:
    def __init__(self, node: Node, statement: Statement):
        self.node = node
        self.statement = statement

    def __str__(self) -> str:
        return f"{self.signature}: {self.text}"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Identifier) and self.signature == value.signature

    def __hash__(self):
        return hash(self.signature)

    @property
    def signature(self) -> str:
        return (
            self.file.signature
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
        return self.statement.file

    @property
    def function(self):
        if self.statement.function is None:
            return None
        if "Function" not in self.statement.function.__class__.__name__:
            return None
        return self.statement.function

    @property
    def references(self) -> list[Identifier]:
        refs = []
        lsp = self.file.project.lsp
        ref_locs = lsp.request_references(
            self.file.relpath, self.start_line - 1, self.start_column - 1
        )
        def_locs = lsp.request_definition(
            self.file.relpath, self.start_line - 1, self.start_column - 1
        )
        ref_locs.extend(def_locs)  # add definition locations to references
        for loc in ref_locs:
            ref_path = loc["relativePath"]
            if ref_path is None:
                continue
            if ref_path not in self.file.project.files:
                continue
            ref_file = self.file.project.files[ref_path]
            ref_line_start_line = loc["range"]["start"]["line"] + 1
            ref_line_start_column = loc["range"]["start"]["character"] + 1
            ref_stats = ref_file.statements_by_line(ref_line_start_line)
            for ref_stat in ref_stats:
                for identifier in ref_stat.identifiers:
                    if (
                        identifier.start_line == ref_line_start_line
                        and identifier.start_column == ref_line_start_column
                    ):
                        refs.append(identifier)
        return sorted(refs, key=lambda x: (x.start_line, x.start_column))

    @property
    def definitions(self) -> list[Identifier]:
        defs = []
        lsp = self.file.project.lsp
        def_locs = lsp.request_definition(
            self.file.relpath, self.start_line - 1, self.start_column - 1
        )
        for loc in def_locs:
            def_path = loc["relativePath"]
            if def_path is None:
                continue
            if def_path not in self.file.project.files:
                continue
            def_file = self.file.project.files[def_path]
            def_line_start_line = loc["range"]["start"]["line"] + 1
            def_line_start_column = loc["range"]["start"]["character"] + 1
            def_stats = def_file.statements_by_line(def_line_start_line)
            for def_stat in def_stats:
                for variable in def_stat.variables:
                    if (
                        variable.start_line == def_line_start_line
                        and variable.start_column == def_line_start_column
                    ):
                        defs.append(variable)
        return sorted(defs, key=lambda x: (x.start_line, x.start_column))

    @cached_property
    def is_taint_from_entry(self) -> bool:
        if self.is_left_value:
            for right_value in self.statement.right_values:
                if right_value.is_taint_from_entry:
                    return True
            return False
        refs = self.references
        backword_refs: list[Identifier] = []
        for ref in refs:
            if ref.start_line < self.start_line:
                backword_refs.append(ref)
        if len(backword_refs) == 0:
            return False
        for ref in backword_refs:
            if (
                "Function" in ref.statement.__class__.__name__
                or "Method" in ref.statement.__class__.__name__
            ):
                return True
            if not ref.is_left_value:
                continue
            for right_value in ref.statement.right_values:
                if right_value.is_taint_from_entry:
                    return True
        return False

    @property
    def is_left_value(self) -> bool:
        parser = self.file.project.parser
        language = self.file.project.language
        stat = self.statement
        query = language.query_left_value(self.text)
        nodes = parser.query_all(stat.node, query)
        for node in nodes:
            if node.start_point == self.node.start_point:
                return True
        return False

    @property
    def is_right_value(self) -> bool:
        return not self.is_left_value


class CIdentifier(Identifier): ...


class JavaIdentifier(Identifier): ...


class PythonIdentifier(Identifier): ...


class JavaScriptIdentifier(Identifier): ...
