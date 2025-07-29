from __future__ import annotations

from ..function import Function
from .statement import PHPBlockStatement


class PHPFunction(Function, PHPBlockStatement): ...
