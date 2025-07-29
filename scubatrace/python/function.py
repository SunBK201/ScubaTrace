from __future__ import annotations

from ..function import Function
from .statement import PythonBlockStatement


class PythonFunction(Function, PythonBlockStatement): ...
