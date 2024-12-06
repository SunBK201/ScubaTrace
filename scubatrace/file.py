from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from tree_sitter import Node

from . import language
from .function import CFunction, Function
from .parser import c_parser
from .statement import Statement
from .structure import CStruct, Struct

if TYPE_CHECKING:
    from .project import Project


class File:
    """
    Represents a file in a project.

    Attributes:
        _path (str): The file path.
        project (Project): The project to which the file belongs.
    """

    def __init__(self, path: str, project: Project):
        """
        Initializes a new instance of the class.

        Args:
            path (str): The file path.
            project (Project): The project associated with this instance.
        """
        self._path = path
        self.project = project

    @property
    def abspath(self) -> str:
        """
        Returns the absolute path of the file.

        Returns:
            str: The absolute path of the file.
        """
        return os.path.abspath(self._path)

    @property
    def relpath(self) -> str:
        """
        Returns the relative path of the file with respect to the project directory.

        The method removes the project directory path from the file's absolute path,
        leaving only the relative path.

        Returns:
            str: The relative path of the file.
        """
        return self._path.replace(self.project.path + "/", "")

    @property
    def text(self) -> str:
        """
        Reads the content of the file at the given path and returns it as a string.

        Returns:
            str: The content of the file.
        """
        with open(self._path, "r") as f:
            return f.read()

    def __str__(self) -> str:
        return self.signature

    @property
    def signature(self) -> str:
        return self.relpath

    @cached_property
    @abstractmethod
    def node(self) -> Node: ...

    @cached_property
    @abstractmethod
    def imports(self) -> list[File]: ...

    @cached_property
    @abstractmethod
    def functions(self) -> list[Function]: ...

    @cached_property
    @abstractmethod
    def structs(self) -> list[Struct]: ...

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]: ...


class CFile(File):
    def __init__(self, path: str, project: Project):
        super().__init__(path, project)

    @cached_property
    def node(self) -> Node:
        return c_parser.parse(self.text)

    @cached_property
    def imports(self) -> list[File]:
        include_node = c_parser.query_all(self.text, language.C.query_include)
        import_files = []
        for node in include_node:
            include_path = node.child_by_field_name("path")
            if include_path is None or include_path.text is None:
                continue
            include_path = include_path.text.decode()
            if include_path[0] == "<":
                continue
            include_path = include_path.strip('"')

            import_file = CFile(
                os.path.join(os.path.dirname(self._path), include_path),
                self.project,
            )
            import_files.append(import_file)
            for file in import_file.imports:
                import_files.append(file)
        return import_files

    @cached_property
    def functions(self) -> list[Function]:
        func_node = c_parser.query_all(self.text, language.C.query_function)
        return [CFunction(node, file=self) for node in func_node]

    @cached_property
    def structs(self) -> list[Struct]:
        struct_node = c_parser.query_all(self.text, language.C.query_struct)
        return [CStruct(node) for node in struct_node]


class CPPFile(File): ...


class JavaFile(File): ...
