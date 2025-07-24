from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

import chardet
from scubalspy import SyncLanguageServer
from tree_sitter import Node

from . import language as lang
from .clazz import Class
from .function import Function
from .identifier import Identifier
from .statement import Statement

if TYPE_CHECKING:
    from .project import Project


class File:
    """
    Represents a source code file in a project.
    """

    project: Project
    """ The project this file belongs to."""

    def __init__(self, path: str, project: Project):
        """
        Initializes a new instance of the class.

        Args:
            path (str): The file path.
            project (Project): The project associated with this instance.
        """
        if path.startswith("file://"):
            path = path[7:]
        self._path = path
        self.project = project
        self.__lsp_preload = False

    @staticmethod
    def File(path: str, project: Project) -> File:
        """
        Factory function to create a :class:`File` instance.

        Args:
            path (str): The file relative path.
            project (Project): The project instance.

        Returns:
            File: An instance of a language-specific File subclass corresponding to the project's language.
        """

        if project.language == lang.C:
            from .cpp.file import CFile

            return CFile(path, project)
        elif project.language == lang.JAVA:
            from .java.file import JavaFile

            return JavaFile(path, project)
        elif project.language == lang.JAVASCRIPT:
            from .javascript.file import JavaScriptFile

            return JavaScriptFile(path, project)
        elif project.language == lang.PYTHON:
            from .python.file import PythonFile

            return PythonFile(path, project)
        elif project.language == lang.GO:
            from .go.file import GoFile

            return GoFile(path, project)
        elif project.language == lang.PHP:
            from .php.file import PHPFile

            return PHPFile(path, project)
        elif project.language == lang.RUBY:
            from .ruby.file import RubyFile

            return RubyFile(path, project)
        elif project.language == lang.RUST:
            from .rust.file import RustFile

            return RustFile(path, project)
        elif project.language == lang.SWIFT:
            from .swift.file import SwiftFile

            return SwiftFile(path, project)
        elif project.language == lang.CSHARP:
            from .csharp.file import CSharpFile

            return CSharpFile(path, project)
        else:
            return File(path, project)

    @property
    def language(self) -> type[lang.Language]:
        """
        The language type associated with the current project.
        """
        return self.project.language

    @property
    def name(self) -> str:
        """
        The name of the file without the directory path.
        """
        return os.path.basename(self._path)

    @property
    def abspath(self) -> str:
        """
        The absolute path of the file.
        """
        return os.path.abspath(self._path)

    @property
    def relpath(self) -> str:
        """
        The relative path of the file with respect to the project directory.
        """
        return self._path.replace(self.project.path + "/", "")

    @property
    def uri(self) -> str:
        """
        The URI of the file.
        """
        return f"file://{self.abspath.replace(os.path.sep, '/')}"

    @property
    def text(self) -> str:
        """
        The content of the file.
        """
        with open(
            self._path,
            "rb",
        ) as f:
            data = f.read()
            encoding = chardet.detect(data)["encoding"]
            if encoding is None:
                encoding = "utf-8"
        with open(
            self._path,
            "r",
            encoding=encoding,
        ) as f:
            return f.read()

    @property
    def lines(self) -> list[str]:
        """
        A list of the lines in the file.
        """
        return self.text.splitlines()

    def __str__(self) -> str:
        return self.signature

    def __hash__(self) -> int:
        return hash(self.signature)

    @property
    def signature(self) -> str:
        return self.relpath

    @property
    def parser(self):
        """
        The parser associated with the current project.
        """
        return self.project.parser

    @cached_property
    def node(self) -> Node:
        """
        The tree-sitter root node for the file.
        """
        return self.parser.parse(self.text)

    @cached_property
    @abstractmethod
    def imports(self) -> list[File]:
        """
        A list of :class:`File` that are imported by this file.

        For example, in Python, this would include files imported using the `import` statement.
        In C/C++, this would include files included using the `#include` directive.
        """
        ...

    @cached_property
    def functions(self) -> list[Function]:
        """
        All functions in the file.
        """
        func_node = self.parser.query_all(self.text, self.language.query_function)
        return [Function.Function(node, file=self) for node in func_node]

    @cached_property
    @abstractmethod
    def classes(self) -> list[Class]: ...

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]:
        """
        All statements of functions in the file.
        """
        stats = []
        for func in self.functions:
            stats.extend(func.statements)
        return stats

    @cached_property
    def identifiers(self) -> list[Identifier]:
        """
        All identifiers of functions in the file.
        """
        identifiers = []
        for stmt in self.statements:
            identifiers.extend(stmt.identifiers)
        return identifiers

    @cached_property
    def variables(self) -> list[Identifier]:
        """
        All variables of functions in the file.
        """
        variables = []
        for stmt in self.statements:
            variables.extend(stmt.variables)
        return variables

    @property
    def is_external(self) -> bool:
        """
        Checks if the file is external (not part of the project).
        """
        return not self.abspath.startswith(self.project.abspath)

    @property
    def lsp(self) -> SyncLanguageServer:
        lsp = self.project.lsp
        if self.__lsp_preload:
            return lsp
        lsp.open_file(self.relpath).__enter__()
        self.__lsp_preload = True

        # preload all imports for the file
        for import_file in self.imports:
            lsp.open_file(import_file.relpath).__enter__()
            # preload corresponding source file if the file is C/C++
            if self.language == lang.C:
                heuristic_name_list = [
                    import_file.name.replace(".h", ".cpp"),
                    import_file.name.replace(".h", ".c"),
                    import_file.name.replace(".hpp", ".cpp"),
                    import_file.name.replace(".hpp", ".c"),
                    import_file.name.replace(".h", ".cc"),
                    import_file.name.replace(".hpp", ".cc"),
                    import_file.name.replace(".c", ".h"),
                    import_file.name.replace(".cpp", ".h"),
                    import_file.name.replace(".c", ".hpp"),
                    import_file.name.replace(".cpp", ".hpp"),
                ]
                for relpath, file in self.project.files.items():
                    for heuristic_name in heuristic_name_list:
                        if relpath.endswith(heuristic_name):
                            lsp.open_file(file.relpath).__enter__()
                            break
        return lsp

    def function_by_line(self, line: int) -> Function | None:
        """
        Returns the function that contains the specified line number.

        Args:
            line (int): The line number to check.

        Returns:
            Function | None: The function that contains the line, or None if not found.
        """
        for func in self.functions:
            if func.start_line <= line <= func.end_line:
                return func
        return None

    def statements_by_line(self, line: int) -> list[Statement]:
        """
        Returns the statements that are located on the specified line number.

        Args:
            line (int): The line number to check.

        Returns:
            list[Statement]: A list of statements that are located on the specified line.
        """
        if line < 1 or line > len(self.lines):
            return []
        func = self.function_by_line(line)
        if func is not None:
            # If the line is in a function, get the statement from the function
            return func.statements_by_line(line)
        else:
            # If the line is not in a function, get the statement from the file
            root_node = self.parser.parse(self.text)
            for node in root_node.named_children:
                if line < node.start_point[0] + 1 or line > node.end_point[0] + 1:
                    continue
                if node.text is None:
                    continue
                return [Statement(node, self)]
        return []
