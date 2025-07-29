from __future__ import annotations

from ..function import Function
from .statement import GoBlockStatement


class GoFunction(Function, GoBlockStatement): ...
