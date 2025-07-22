import tree_sitter_swift as tsswift
from tree_sitter import Language as TSLanguage

from ..language import Language


class SWIFT(Language):
    extensions = ["swift"]
    tslanguage = TSLanguage(tsswift.language())
