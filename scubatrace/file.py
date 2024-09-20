from __future__ import annotations

import os
from abc import abstractmethod
from parser import c_parser
from structure import CStruct, Struct

import language
from function import CFunction, Function


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

    @property
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


class CFile(File):
    def __init__(self, path: str):
        super().__init__(path)
    
    @property
    def imports(self) -> list[File]:
        ...

    @property
    def functions(self) -> list[Function]:
        func_node = c_parser.query_all(self.text, language.C.query_function)
        return [CFunction(node) for node in func_node]

    @property
    def structs(self) -> list[Struct]:
        struct_node = c_parser.query_all(self.text, language.C.query_struct)
        return [CStruct(node) for node in struct_node]


class CPPFile(File):
    ...


class JavaFile(File):
    ...
