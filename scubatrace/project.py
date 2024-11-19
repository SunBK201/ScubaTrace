import os
from functools import cached_property

from . import language
from .file import CFile, CPPFile, File, JavaFile
from .function import Function


class Project:
    def __int__(self, path: str, language: type[language.Language]):
        """
        Initialize the project with the given path and language.

        Args:
            path (str): The file path of the project.
            language (type[language.Language]): The programming language used in the project.
        """
        self.path = path
        self.language = language

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
                    elif self.language == language.CPP:
                        file_lists[key] = CPPFile(file_path, self)
                    elif self.language == language.JAVA:
                        file_lists[key] = JavaFile(file_path, self)
        return file_lists

    @cached_property
    def functions(self) -> list[Function]:
        functions = []
        for file in self.files.values():
            functions.extend(file.functions)
        return functions


class CProject(Project):
    def __init__(self, path: str):
        super().__int__(path, language.C)


if __name__ == "__main__":
    a_proj = CProject("../tests")
    print(a_proj.files["test.c"])
