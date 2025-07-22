import tree_sitter_ruby as tsruby
from tree_sitter import Language as TSLanguage

from ..language import Language


class RUBY(Language):
    extensions = ["rb"]
    tslanguage = TSLanguage(tsruby.language())
