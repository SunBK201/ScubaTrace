from __future__ import annotations

import atexit
import os
from abc import abstractmethod
from collections import deque
from functools import cached_property

import networkx as nx
from scubalspy import SyncLanguageServer
from scubalspy.scubalspy_config import ScubalspyConfig
from scubalspy.scubalspy_logger import ScubalspyLogger

from . import language as lang
from .file import File
from .function import Function, FunctionDeclaration
from .parser import Parser


class Project:
    """
    A codebase project with a specified path and language.
    """

    path: str
    """The file system path to the project root."""
    language: type[lang.Language]
    """The programming language type for the project."""

    @staticmethod
    def create(
        path: str,
        language: type[lang.Language],
        enable_lsp: bool = True,
    ) -> Project:
        """
        Factory function to create a language-specific :class:`Project` instance.

        Args:
            path (str): The file system path to the project root.
            language (type[Language]): The programming language type for the project.
            enable_lsp (bool, optional): Whether to enable Language Server Protocol (LSP) support. Defaults to True.
                Note: For PHP and Swift, LSP is always disabled.

        Returns:
            Project: An instance of the appropriate language-specific Project subclass.

        Raises:
            ValueError: If the provided language is not supported.
        """
        if language == lang.C:
            from .cpp.project import CProject

            return CProject(path, enable_lsp)
        elif language == lang.JAVA:
            from .java.project import JavaProject

            return JavaProject(path, enable_lsp)
        elif language == lang.PYTHON:
            from .python.project import PythonProject

            return PythonProject(path, enable_lsp)
        elif language == lang.JAVASCRIPT:
            from .javascript.project import JavaScriptProject

            return JavaScriptProject(path, enable_lsp)
        elif language == lang.GO:
            from .go.project import GoProject

            return GoProject(path, enable_lsp)
        elif language == lang.RUST:
            from .rust.project import RustProject

            return RustProject(path, enable_lsp)
        elif language == lang.CSHARP:
            from .csharp.project import CSharpProject

            return CSharpProject(path, enable_lsp)
        elif language == lang.RUBY:
            from .ruby.project import RubyProject

            return RubyProject(path, enable_lsp)
        elif language == lang.PHP:
            from .php.project import PHPProject

            return PHPProject(path, enable_lsp=False)
        elif language == lang.SWIFT:
            from .swift.project import SwiftProject

            return SwiftProject(path, enable_lsp=False)
        else:
            raise ValueError("Unsupported language for project creation")

    def __init__(
        self,
        path: str,
        language: type[lang.Language],
        enable_lsp: bool = True,
    ):
        self.path = path
        self.language = language
        if enable_lsp:
            self.start_lsp()

    def start_lsp(self):
        if self.language == lang.C:
            lsp_language = "cpp"
        elif self.language == lang.JAVA:
            lsp_language = "java"
        elif self.language == lang.PYTHON:
            lsp_language = "python"
        elif self.language == lang.JAVASCRIPT:
            lsp_language = "javascript"
        elif self.language == lang.GO:
            lsp_language = "go"
        elif self.language == lang.RUST:
            lsp_language = "rust"
        elif self.language == lang.CSHARP:
            lsp_language = "csharp"
        elif self.language == lang.RUBY:
            lsp_language = "ruby"
        elif self.language == lang.PHP:
            lsp_language = "php"
            return
        elif self.language == lang.SWIFT:
            lsp_language = "swift"
            return
        else:
            raise ValueError("Unsupported language")
        self.lsp = SyncLanguageServer.create(
            ScubalspyConfig.from_dict({"code_language": lsp_language}),
            ScubalspyLogger(),
            os.path.abspath(self.path),
        )
        if self.language == lang.C:
            self.conf_file = os.path.join(self.path, "compile_flags.txt")
            if not os.path.exists(self.conf_file):
                with open(self.conf_file, "w") as f:
                    for sub_dir in self.sub_dirs:
                        f.write(f"-I{sub_dir}\n")
                atexit.register(os.remove, self.conf_file)
        self.lsp.sync_start_server()

    @property
    def abspath(self) -> str:
        """
        The absolute path of the project.
        """
        return os.path.abspath(self.path)

    @property
    def sub_dirs(self) -> list[str]:
        """
        A list of subdirectories in the project path.
        """
        sub_dirs = []
        for root, dirs, _ in os.walk(self.path):
            for dir in dirs:
                sub_dirs.append(os.path.join(root, dir))
        return sub_dirs

    @property
    @abstractmethod
    def parser(self) -> Parser:
        """
        The :class:`Parser` instance associated with the current object.
        """
        ...

    @cached_property
    def files(self) -> dict[str, File]:
        """
        A dictionary mapping relative file paths to :class:`File` objects for all source files in the project.

        The keys are relative paths from the project root, and the values are :class:`File` representing each source file.
        """
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    file_lists[key] = File.create(file_path, self)
        return file_lists

    @cached_property
    def files_abspath(self) -> dict[str, File]:
        """
        A dictionary mapping the absolute file paths to their corresponding :class:`File` objects.
        """
        return {v.abspath: v for v in self.files.values()}

    @cached_property
    def files_uri(self) -> dict[str, File]:
        """
        A dictionary mapping the file URIs to their corresponding :class:`File` objects.
        """
        return {"file://" + v.abspath: v for v in self.files.values()}

    @cached_property
    def functions(self) -> list[Function]:
        """
        Functions in the project.
        """
        functions = []
        for file in self.files.values():
            functions.extend(file.functions)
        return functions

    @cached_property
    @abstractmethod
    def entry_point(self) -> Function | None:
        """
        The entry point function of the project, if it exists.

        For example, in a C project, this would be the `main` function.
        If no entry point is defined, returns None.
        """
        ...

    def __build_callgraph(self, entry: Function) -> nx.MultiDiGraph:
        cg = nx.MultiDiGraph()
        dq: deque[Function | FunctionDeclaration] = deque([entry])
        visited: set[Function | FunctionDeclaration] = set([entry])
        while len(dq) > 0:
            caller = dq.popleft()
            if isinstance(caller, FunctionDeclaration):
                continue
            if caller.file.is_external:
                continue
            for callee, callsites in caller.callees.items():
                if callee in visited:
                    continue
                visited.add(callee)
                cg.add_node(
                    callee,
                    label=callee.dot_text,
                )
                for callsite in callsites:
                    cg.add_edge(
                        caller,
                        callee,
                        line=callsite.start_line,
                        column=callsite.start_column,
                    )
                dq.append(callee)
        return cg

    @property
    def callgraph(self) -> nx.MultiDiGraph:
        """
        Call graph of the project, starting from the entry point function.
        """
        entry = self.entry_point
        if entry is None:
            return nx.MultiDiGraph()
        for file in self.files.values():
            try:
                self.lsp.open_file(file.relpath).__enter__()
            except Exception as e:
                print(f"Error preloading file {file.relpath}: {e}")
        cg = self.__build_callgraph(entry)
        return cg

    def export_callgraph(self, output_path: str):
        """
        Exports the call graph of the project to a DOT file.

        Args:
            output_path (str): The directory where the call graph DOT file will be saved.
        """
        os.makedirs(output_path, exist_ok=True)
        callgraph_path = os.path.join(output_path, "callgraph.dot")
        nx.nx_agraph.write_dot(self.callgraph, callgraph_path)

    def search_function(self, file: str, start_line: int) -> Function | None:
        for func in self.files[file].functions:
            if func.start_line <= start_line <= func.end_line:
                return func
        return None
