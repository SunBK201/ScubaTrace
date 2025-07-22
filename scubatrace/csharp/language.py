import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language as TSLanguage

from ..language import Language


class CSHARP(Language):
    extensions = ["cs"]
    tslanguage = TSLanguage(tscsharp.language())
