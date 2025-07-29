from __future__ import annotations

from ..function import Function
from .statement import SwiftBlockStatement


class SwiftFunction(Function, SwiftBlockStatement): ...
