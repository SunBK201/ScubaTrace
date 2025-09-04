from __future__ import annotations

from functools import cached_property

from ..identifier import Identifier
from ..statement import BlockStatement, SimpleStatement, Statement


class PythonSimpleStatement(SimpleStatement):
    @cached_property
    def right_uncle_ancestor(self) -> Statement | None:
        """
        Returns the right uncle ancestor of the statement.

        The right uncle ancestor is the next statement in the control flow after this statement.
        """
        from ..function import Function

        cur = self.parent
        while cur is not None:
            if isinstance(cur, Function):
                return None
            if not isinstance(cur, Statement):
                return None
            if cur.node_type in self.language.LOOP_STATEMENTS:
                return cur
            if (
                cur.next_sibling is not None
                and cur.next_sibling.field_name != "alternative"
            ):
                return cur.next_sibling
            cur = cur.parent
        return None

    @cached_property
    def variables(self) -> list[Identifier]:
        """
        Variables in the statement.
        """
        variables = []
        for identifier in self.identifiers:
            node = identifier.node
            parent = node.parent
            if parent is not None:
                if parent.type in [
                    "ERROR",
                    "call",
                    "function_definition",
                ]:
                    continue
                if (
                    parent.type == "keyword_argument"
                    and parent.child_by_field_name("name") == node
                ):
                    continue
            variables.append(identifier)
        return variables


class PythonBlockStatement(BlockStatement):
    @cached_property
    def right_uncle_ancestor(self) -> Statement | None:
        """
        Returns the right uncle ancestor of the statement.

        The right uncle ancestor is the next statement in the control flow after this statement.
        """
        from ..function import Function

        cur = self.parent
        while cur is not None:
            if isinstance(cur, Function):
                return None
            if not isinstance(cur, Statement):
                return None
            if cur.node_type in self.language.LOOP_STATEMENTS:
                return cur
            if (
                cur.next_sibling is not None
                and cur.next_sibling.field_name != "alternative"
            ):
                return cur.next_sibling
            cur = cur.parent
        return None
