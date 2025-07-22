import tree_sitter_php as tsphp
from tree_sitter import Language as TSLanguage

from ..language import Language


class PHP(Language):
    extensions = ["php"]
    tslanguage = TSLanguage(tsphp.language_php())
