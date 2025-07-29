from __future__ import annotations

from ..function import Function
from .statement import RustBlockStatement


class RustFunction(Function, RustBlockStatement): ...
