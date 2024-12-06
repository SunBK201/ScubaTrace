import os
from functools import cached_property

from . import language
from .file import CFile, CPPFile, File, JavaFile
from .function import Function


class Project:
    """
    Represents a programming project with a specified path and language.
    """

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
        """
        Retrieves a dictionary of files in the project directory that match the specified language extensions.

        This method walks through the directory tree starting from the project's path and collects files
        that have extensions matching the language's extensions. It then creates instances of the appropriate
        file class (CFile, CPPFile, JavaFile) based on the language and stores them in a dictionary.

        Returns:
            dict[str, File]: A dictionary where the keys are relative file paths and the values are instances
                             of the corresponding file class (CFile, CPPFile, JavaFile).
        """
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
    """
    Representing a C language project.

    Attributes:
        path (str): The file path to the project.
    """

    def __init__(self, path: str):
        super().__int__(path, language.C)


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
