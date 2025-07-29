from __future__ import annotations

from ..function import Function
from .statement import JavaBlockStatement


class JavaFunction(Function, JavaBlockStatement): ...
