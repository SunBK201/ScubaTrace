from __future__ import annotations

import os
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

import chardet
from scubalspy import SyncLanguageServer
from tree_sitter import Node

from . import language
from .clazz import Class, CPPClass, JavaClass, JavaScriptClass, PythonClass
from .function import CFunction, Function, JavaScriptFunction, PythonFunction
from .identifier import Identifier
from .parser import cpp_parser, java_parser, javascript_parser, python_parser
from .statement import Statement
from .structure import CStruct, Struct

if TYPE_CHECKING:
    from .project import JavaProject, JavaScriptProject, Project, PythonProject


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
        self.__lsp_preload = False

    @property
    def language(self) -> type[language.Language]:
        return self.project.language

    @property
    def name(self) -> str:
        """
        Returns the name of the file without the directory path.

        Returns:
            str: The name of the file.
        """
        return os.path.basename(self._path)

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
    def uri(self) -> str:
        """
        Returns the URI of the file.

        The URI is constructed by replacing the project path with "file://" and
        ensuring it is properly formatted for use in a URI context.

        Returns:
            str: The URI of the file.
        """
        return f"file://{self.abspath.replace(os.path.sep, '/')}"

    @property
    def text(self) -> str:
        """
        Reads the content of the file at the given path and returns it as a string.

        Returns:
            str: The content of the file.
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
        Reads the content of the file and returns it as a list of lines.

        Returns:
            list[str]: The content of the file split into lines.
        """
        return self.text.splitlines()

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
    def classes(self) -> list[Class]: ...

    @cached_property
    @abstractmethod
    def structs(self) -> list[Struct]: ...

    @cached_property
    @abstractmethod
    def statements(self) -> list[Statement]: ...

    @cached_property
    @abstractmethod
    def identifiers(self) -> list[Identifier]: ...

    @cached_property
    @abstractmethod
    def variables(self) -> list[Identifier]: ...

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
            if self.language == language.CPP or self.language == language.C:
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
        for func in self.functions:
            if func.start_line <= line <= func.end_line:
                return func
        return None

    def statements_by_line(self, line: int) -> list[Statement]:
        if line < 1 or line > len(self.lines):
            return []
        func = self.function_by_line(line)
        if func is not None:
            # If the line is in a function, get the statement from the function
            return func.statements_by_line(line)
        else:
            # If the line is not in a function, get the statement from the file
            root_node = self.project.parser.parse(self.text)
            for node in root_node.named_children:
                if line < node.start_point[0] + 1 or line > node.end_point[0] + 1:
                    continue
                if node.text is None:
                    continue
                return [Statement(node, self)]
        return []


class CFile(File):
    def __init__(self, path: str, project: Project):
        super().__init__(path, project)

    @cached_property
    def node(self) -> Node:
        return cpp_parser.parse(self.text)

    @cached_property
    def imports(self) -> list[File]:
        include_node = cpp_parser.query_all(self.text, language.C.query_include)
        import_files = []
        for node in include_node:
            include_path_node = node.child_by_field_name("path")
            if include_path_node is None:
                continue
            include = self.lsp.request_definition(
                self.relpath,
                include_path_node.start_point[0],
                include_path_node.start_point[1],
            )
            if len(include) == 0:
                continue
            include = include[0]
            include_abspath = include["absolutePath"]
            import_files.append(self.project.files_abspath[include_abspath])
        return import_files

    @cached_property
    def source_header(self) -> File | None:
        """
        switch between the main source file (*.cpp) and header (*.h)
        """
        uri = self.lsp.request_switch_source_header(self.relpath, self.uri)
        if len(uri) == 0:
            return None
        return self.project.files_uri.get(uri, None)

    @cached_property
    def functions(self) -> list[Function]:
        func_node = cpp_parser.query_all(self.text, language.CPP.query_function)
        return [CFunction(node, file=self) for node in func_node]

    @cached_property
    def structs(self) -> list[Struct]:
        struct_node = cpp_parser.query_all(self.text, language.CPP.query_struct)
        return [CStruct(node) for node in struct_node]

    @cached_property
    def statements(self) -> list[Statement]:
        stats = []
        for func in self.functions:
            stats.extend(func.statements)
        return stats

    @cached_property
    def identifiers(self) -> list[Identifier]:
        identifiers = []
        for stmt in self.statements:
            identifiers.extend(stmt.identifiers)
        return identifiers


class CPPFile(CFile):
    def __init__(self, path: str, project: Project):
        super().__init__(path, project)

    @cached_property
    def classes(self) -> list[Class]:
        class_node = cpp_parser.query_all(self.text, language.CPP.query_class)
        return [CPPClass(node, file=self) for node in class_node]


class JavaFile(File):
    def __init__(self, path: str, project: JavaProject):
        super().__init__(path, project)

    @cached_property
    def node(self) -> Node:
        return java_parser.parse(self.text)

    @property
    def package(self) -> str:
        package_node = java_parser.query_oneshot(self.text, language.JAVA.query_package)
        if package_node is None:
            return ""
        package = package_node.text.decode()  # type: ignore
        return package

    @cached_property
    def import_class(self) -> list[str]:
        import_node = java_parser.query_all(self.text, language.JAVA.query_import)
        imports = []
        for node in import_node:
            assert node.text is not None
            scoped_identifier = node.text.decode()
            imports.append(scoped_identifier)
        return imports

    @cached_property
    def classes(self) -> list[Class]:
        class_node = java_parser.query_all(self.text, language.JAVA.query_class)
        return [JavaClass(node, file=self) for node in class_node]


class PythonFile(File):
    def __init__(self, path: str, project: PythonProject):
        super().__init__(path, project)

    @cached_property
    def node(self) -> Node:
        return python_parser.parse(self.text)

    @cached_property
    def functions(self) -> list[Function]:
        func_node = python_parser.query_all(self.text, language.PYTHON.query_function)
        return [PythonFunction(node, file=self) for node in func_node]

    @cached_property
    def classes(self) -> list[Class]:
        class_node = python_parser.query_all(self.text, language.PYTHON.query_class)
        return [PythonClass(node, file=self) for node in class_node]


class JavaScriptFile(File):
    def __init__(self, path: str, project: JavaScriptProject):
        super().__init__(path, project)

    @cached_property
    def node(self) -> Node:
        return javascript_parser.parse(self.text)

    @cached_property
    def functions(self) -> list[Function]:
        func_node = javascript_parser.query_all(
            self.text, language.JAVASCRIPT.query_function
        )
        return [JavaScriptFunction(node, file=self) for node in func_node]

    @cached_property
    def classes(self) -> list[Class]:
        class_node = javascript_parser.query_all(
            self.text, language.JAVASCRIPT.query_class
        )
        return [JavaScriptClass(node, file=self) for node in class_node]
