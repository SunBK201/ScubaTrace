import os
from functools import cached_property

from multilspy import SyncLanguageServer
from multilspy.multilspy_config import MultilspyConfig
from multilspy.multilspy_logger import MultilspyLogger

from . import language
from .file import CFile, CPPFile, File, JavaFile, JavaScriptFile, PythonFile
from .function import Function
from .language import CPP, JAVA, JAVASCRIPT, PYTHON, C


class Project:
    """
    Represents a programming project with a specified path and language.
    """

    def __int__(
        self, path: str, language: type[language.Language], enable_lsp: bool = False
    ):
        """
        Initialize the project with the given path and language.

        Args:
            path (str): The file path of the project.
            language (type[language.Language]): The programming language used in the project.
        """
        self.path = path
        self.language = language
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
                MultilspyConfig.from_dict({"code_language": lsp_language}),
                MultilspyLogger(),
                os.path.abspath(path),
            )
            self.lsp.sync_start_server()

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


class CProject(Project):
    def __init__(self, path: str, enable_lsp: bool = False):
        super().__int__(path, language.C, enable_lsp)

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
        super().__int__(path, language.CPP, enable_lsp)

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
        super().__int__(path, language.JAVA, enable_lsp)

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
        super().__int__(path, language.PYTHON, enable_lsp)

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
        super().__int__(path, language.JAVASCRIPT, enable_lsp)

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
