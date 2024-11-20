from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from . import language
from .function import CFunction, Function
from .parser import c_parser
from .structure import CStruct, Struct

if TYPE_CHECKING:
    from .project import Project


class File:
    def __init__(self, path: str, project: Project):
        self._path = path
        self.project = project

    @property
    def abspath(self) -> str:
        return os.path.abspath(self._path)

    @property
    def relpath(self) -> str:
        return self._path.replace(self.project.path + "/", "")

    @property
    def text(self) -> str:
        with open(self._path, "r") as f:
            return f.read()

    def __str__(self) -> str:
        return self.relpath

    @cached_property
    @abstractmethod
    def imports(self) -> list[File]: ...

    @property
    @abstractmethod
    def functions(self) -> list[Function]: ...

    @property
    @abstractmethod
    def structs(self) -> list[Struct]: ...


class CFile(File):
    def __init__(self, path: str, project: Project):
        super().__init__(path, project)

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

    @property
    def functions(self) -> list[Function]:
        func_node = c_parser.query_all(self.text, language.C.query_function)
        return [CFunction(node, file=self) for node in func_node]

    @property
    def structs(self) -> list[Struct]:
        struct_node = c_parser.query_all(self.text, language.C.query_struct)
        return [CStruct(node) for node in struct_node]


class CPPFile(File): ...


class JavaFile(File): ...
