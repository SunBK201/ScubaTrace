from __future__ import annotations

from ..function import Function
from .statement import RubyBlockStatement


class RubyFunction(Function, RubyBlockStatement): ...
