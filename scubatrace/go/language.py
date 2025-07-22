import tree_sitter_go as tsgo
from tree_sitter import Language as TSLanguage

from ..language import Language


class GO(Language):
    extensions = ["go"]
    tslanguage = TSLanguage(tsgo.language())
