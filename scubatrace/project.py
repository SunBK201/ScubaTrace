import os
from functools import cached_property

import networkx as nx
from scubalspy import SyncLanguageServer
from scubalspy.scubalspy_config import ScubalspyConfig
from scubalspy.scubalspy_logger import ScubalspyLogger

from . import joern, language
from .call import Call
from .file import CFile, CPPFile, File, JavaFile, JavaScriptFile, PythonFile
from .function import Function
from .language import CPP, JAVA, JAVASCRIPT, PYTHON, C


class Project:
    """
    Represents a programming project with a specified path and language.
    """

    def __init__(
        self,
        path: str,
        language: type[language.Language],
        enable_lsp: bool = False,
        enable_joern: bool = False,
    ):
        self.path = path
        self.language = language
        if enable_joern:
            if language == C or language == CPP:
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
            if language == C or language == CPP:
                lsp_language = "cpp"
            elif language == JAVA:
                lsp_language = "java"
            elif language == PYTHON:
                lsp_language = "python"
            elif language == JAVASCRIPT:
                lsp_language = "javascript"
            else:
                raise ValueError("Unsupported language")
            self.lsp = SyncLanguageServer.create(
                ScubalspyConfig.from_dict({"code_language": lsp_language}),
                ScubalspyLogger(),
                os.path.abspath(path),
            )
            self.lsp.sync_start_server()

    def close(self):
        if self.joern is not None:
            self.joern.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @cached_property
    def files(self) -> dict[str, File]:
        """
        Retrieves a dictionary of files in the project directory that match the specified language extensions.

        This method walks through the directory tree starting from the project's path and collects files
        that have extensions matching the language's extensions. It then creates instances of the appropriate
        file class (CFile, CPPFile, JavaFile) based on the language and stores them in a dictionary.

        Returns:
            dict[str, File]: A dictionary where the keys are relative file paths and the values are instances
                             of the corresponding file class (CFile, CPPFile, JavaFile).
        """
        ...

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
    def callgraph(self) -> nx.MultiDiGraph:
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
            src_func.callees.append(
                Call(
                    src_func,
                    dst_func,
                    int(data["LINE_NUMBER"]),
                    int(data["COLUMN_NUMBER"]),
                )
            )
            dst_func.callers.append(
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
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__init__(path, language.C, enable_lsp=enable_lsp)

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


class CPPProject(Project):
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__init__(path, language.CPP, enable_lsp)

    @cached_property
    def files(self) -> dict[str, File]:
        file_lists = {}
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    file_path = os.path.join(root, file)
                    key = file_path.replace(self.path + "/", "")
                    if self.language == language.CPP:
                        file_lists[key] = CPPFile(file_path, self)
        return file_lists


class JavaProject(Project):
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__init__(path, language.JAVA, enable_lsp)

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
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__init__(path, language.PYTHON, enable_lsp)

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
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__init__(path, language.JAVASCRIPT, enable_lsp)

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


def testPreControl():
    a_proj = CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[0]
    posts = func_main.statements[3].post_controls
    print(posts)
    for post in posts:
        print(post.text)


if __name__ == "__main__":
    testPreControl()
