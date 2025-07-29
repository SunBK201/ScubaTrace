from __future__ import annotations

from ..function import Function
from .statement import CSharpBlockStatement


class CSharpFunction(Function, CSharpBlockStatement): ...
