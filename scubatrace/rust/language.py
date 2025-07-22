import tree_sitter_rust as tsrust
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUST(Language):
    extensions = ["rs"]
    tslanguage = TSLanguage(tsrust.language())
