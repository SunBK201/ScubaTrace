import atexit
import os
from abc import abstractmethod
from collections import deque
from functools import cached_property

import networkx as nx
from scubalspy import SyncLanguageServer
from scubalspy.scubalspy_config import ScubalspyConfig
from scubalspy.scubalspy_logger import ScubalspyLogger

from . import joern, language
from .call import Call
from .file import CFile, File, JavaFile, JavaScriptFile, PythonFile
from .function import Function, FunctionDeclaration
from .language import JAVA, JAVASCRIPT, PYTHON, C
from .parser import Parser, c_parser, java_parser, javascript_parser, python_parser


class Project:
    """
    Represents a programming project with a specified path and language.
    """

    def __init__(
        self,
        path: str,
        language: type[language.Language],
        enable_lsp: bool = True,
        enable_joern: bool = False,
    ):
        self.path = path
        self.language = language
        if enable_joern:
            if language == C:
                joern_language = joern.Language.C
            elif language == JAVA:
                joern_language = joern.Language.JAVA
            elif language == PYTHON:
                joern_language = joern.Language.PYTHON
            elif language == JAVASCRIPT:
                joern_language = joern.Language.JAVASCRIPT
            else:
                raise ValueError("Joern unsupported language")
            self.joern = joern.Joern(
                path,
                joern_language,
            )
            self.joern.export_with_preprocess()
        if enable_lsp:
            self.start_lsp()

    def start_lsp(self):
        if self.language == C:
            lsp_language = "cpp"
        elif self.language == JAVA:
            lsp_language = "java"
        elif self.language == PYTHON:
            lsp_language = "python"
        elif self.language == JAVASCRIPT:
            lsp_language = "javascript"
        else:
            raise ValueError("Unsupported language")
        self.lsp = SyncLanguageServer.create(
            ScubalspyConfig.from_dict({"code_language": lsp_language}),
            ScubalspyLogger(),
            os.path.abspath(self.path),
        )
        if self.language == C:
            self.conf_file = os.path.join(self.path, "compile_flags.txt")
            if not os.path.exists(self.conf_file):
                with open(self.conf_file, "w") as f:
                    for sub_dir in self.sub_dirs:
                        f.write(f"-I{sub_dir}\n")
                atexit.register(os.remove, self.conf_file)
        self.lsp.sync_start_server()

    def close(self):
        if "joern" in self.__dict__:
            self.joern.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def abspath(self) -> str:
        return os.path.abspath(self.path)

    @property
    def sub_dirs(self) -> list[str]:
        """
        Returns a list of subdirectories in the project path.
        """
        sub_dirs = []
        for root, dirs, _ in os.walk(self.path):
            for dir in dirs:
                sub_dirs.append(os.path.join(root, dir))
        return sub_dirs

    @property
    @abstractmethod
    def parser(self) -> Parser: ...

    @cached_property
    def files(self) -> dict[str, File]: ...

    @cached_property
    def files_abspath(self) -> dict[str, File]:
        return {v.abspath: v for v in self.files.values()}

    @cached_property
    def files_uri(self) -> dict[str, File]:
        """
        Returns a dictionary of files in the project with 'file://' URIs as keys.
        This is useful for accessing files in a URI format.
        """
        return {"file://" + v.abspath: v for v in self.files.values()}

    @cached_property
    def functions(self) -> list[Function]:
        """
        Retrieve a list of all functions from the files in the project.

        This method iterates over all files in the project and collects
        all functions defined in those files.

        Returns:
            list[Function]: A list of Function objects from all files in the project.
        """
        functions = []
        for file in self.files.values():
            functions.extend(file.functions)
        return functions

    @cached_property
    @abstractmethod
    def entry_point(self) -> Function | None: ...

    def __build_callgraph(self, entry: Function) -> nx.MultiDiGraph:
        """
        Build a call graph starting from the given entry function.

        Args:
            entry (Function | None): The entry point function to start building the call graph.

        Returns:
            nx.MultiDiGraph: A directed graph representing the call relationships between functions.
        """
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
            caller.calls
        return cg

    @property
    def callgraph(self) -> nx.MultiDiGraph:
        entry = self.entry_point
        if entry is None:
            return nx.MultiDiGraph()
        cg = self.__build_callgraph(entry)
        return cg

    @cached_property
    def callgraph_joern(self) -> nx.MultiDiGraph:
        if self.joern is None:
            raise ValueError("Joern is not enabled for this project.")
        joern_cg = self.joern.callgraph
        cg = nx.MultiDiGraph()
        for node in joern_cg.nodes:
            if joern_cg.nodes[node]["NODE_TYPE"] != "METHOD":
                continue
            if joern_cg.nodes[node]["IS_EXTERNAL"] == "true":
                continue
            func = self.search_function(
                joern_cg.nodes[node]["FILENAME"],
                int(joern_cg.nodes[node]["LINE_NUMBER"]),
            )
            if func is None:
                continue
            func.set_joernid(node)
            cg.add_node(
                func,
                label=func.dot_text,
            )
        for u, v, data in joern_cg.edges(data=True):
            if joern_cg.nodes[u]["NODE_TYPE"] != "METHOD":
                continue
            if joern_cg.nodes[v]["NODE_TYPE"] != "METHOD":
                continue

            # search by joern_id
            src_func: Function | None = None
            dst_func: Function | None = None
            for node in cg.nodes:
                if node.joern_id == u:
                    src_func = node
                if node.joern_id == v:
                    dst_func = node
            if src_func is None or dst_func is None:
                continue
            if src_func == dst_func:
                continue
            src_func.callees_joern.append(
                Call(
                    src_func,
                    dst_func,
                    int(data["LINE_NUMBER"]),
                    int(data["COLUMN_NUMBER"]),
                )
            )
            dst_func.callers_joern.append(
                Call(
                    src_func,
                    dst_func,
                    int(data["LINE_NUMBER"]),
                    int(data["COLUMN_NUMBER"]),
                )
            )
            cg.add_edge(
                src_func,
                dst_func,
                **data,
            )
        return cg

    def export_callgraph(self, output_path: str):
        os.makedirs(output_path, exist_ok=True)
        callgraph_path = os.path.join(output_path, "callgraph.dot")
        nx.nx_agraph.write_dot(self.callgraph, callgraph_path)

    def search_function(self, file: str, start_line: int) -> Function | None:
        for func in self.files[file].functions:
            if func.start_line <= start_line <= func.end_line:
                return func
        return None


class CProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.C, enable_lsp=enable_lsp)

    @property
    def parser(self) -> Parser:
        return c_parser

    @cached_property
    def files(self) -> dict[str, File]:
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    if self.language == language.C:
                        file_lists[key] = CFile(file_path, self)
        return file_lists

    @cached_property
    def entry_point(self) -> Function | None:
        for func in self.functions:
            if func.name == "main":
                return func
        return None


class JavaProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.JAVA, enable_lsp)

    @property
    def parser(self) -> Parser:
        return java_parser

    @cached_property
    def files(self) -> dict[str, File]:
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    if self.language == language.JAVA:
                        file_lists[key] = JavaFile(file_path, self)
        return file_lists

    @property
    def class_path(self) -> str:
        return self.path


class PythonProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.PYTHON, enable_lsp)

    @property
    def parser(self) -> Parser:
        return python_parser

    @cached_property
    def files(self) -> dict[str, File]:
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    if self.language == language.PYTHON:
                        file_lists[key] = PythonFile(file_path, self)
        return file_lists


class JavaScriptProject(Project):
    def __init__(self, path: str, enable_lsp: bool = True):
        super().__init__(path, language.JAVASCRIPT, enable_lsp)

    @property
    def parser(self) -> Parser:
        return javascript_parser

    @cached_property
    def files(self) -> dict[str, File]:
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    if self.language == language.JAVASCRIPT:
                        file_lists[key] = JavaScriptFile(file_path, self)
        return file_lists
