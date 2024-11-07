from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from parser import c_parser
from typing import TYPE_CHECKING

import language
from structure import CStruct, Struct

if TYPE_CHECKING:
    from function import CFunction, Function
    from project import Project


class File:
    def __init__(self, path: str, project: Project):
        self.__path = path
        self.project = project

    @property
    def abspath(self) -> str:
        return os.path.abspath(self.__path)

    @property
    def relpath(self) -> str:
        return self.__path.replace(self.project.path + "/", "")

    @property
    def text(self) -> str:
        with open(self.__path, "r") as f:
            return f.read()

    def __str__(self) -> str:
        return self.relpath

    @cached_property
    @abstractmethod
    def imports(self) -> list[File]: ...

    @property
    @abstractmethod
    def exports(self) -> list[File]: ...

    @property
    @abstractmethod
    def functions(self) -> list[Function]: ...

    @property
    @abstractmethod
    def structs(self) -> list[Struct]: ...

    @property
    @abstractmethod
    def accessible_files(self) -> list[File]: ...


class CFile(File):
    def __init__(self, path: str, project: Project):
        super().__init__(path, project)

    @cached_property
    def imports(self) -> list[File]:
        # TODO
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

            import_files.append(
                CFile(
                    os.path.join(os.path.dirname(self.__path), include_path),
                    self.project,
                )
            )
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
