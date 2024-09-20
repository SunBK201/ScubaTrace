import os
from functools import cached_property

import language
from file import CFile, CPPFile, File, JavaFile
from function import Function


class Project:
    def __int__(self, path: str, language: type[language.Language]):
        self.path = path
        self.language = language

    @cached_property
    def files(self) -> list[File]:
        file_lists = []
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.split(".")[-1] in self.language.extensions:
                    if self.language == language.C:
                        file_lists.append(CFile(os.path.join(root, file)))
                    elif self.language == language.CPP:
                        file_lists.append(CPPFile(os.path.join(root, file)))
                    elif self.language == language.JAVA:
                        file_lists.append(JavaFile(os.path.join(root, file)))
        return file_lists

    @cached_property
    def functions(self) -> list[Function]:
        functions = []
        for file in self.files:
            functions.extend(file.functions)
        return functions


class CProject(Project):
    def __init__(self, path: str):
        super().__int__(path, language.C)


if __name__ == '__main__':
    a_proj = CProject("../tests")
    print(a_proj.files[0].structs[0].name)
