from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Generator

from tree_sitter import Node

from ..statement import BlockStatement, SimpleStatement

if TYPE_CHECKING:
    from ..file import File
    from ..function import Function
    from ..statement import Statement


class SwiftSimpleStatement(SimpleStatement): ...


class SwiftBlockStatement(BlockStatement): ...
