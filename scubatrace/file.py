from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from parser import c_parser

import language
from function import CFunction, Function
from structure import CStruct, Struct


class File:
    def __init__(self, path: str):
        self.path = path

    @property
    def abspath(self) -> str:
        return os.path.abspath(self.path)

    @property
    def relpath(self) -> str:
        return os.path.relpath(self.path)

    @property
    def text(self) -> str:
        with open(self.path, "r") as f:
            return f.read()

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
    def __init__(self, path: str):
        super().__init__(path)

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
            import_files.append(
                CFile(os.path.join(os.path.dirname(self.path), include_path))
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
