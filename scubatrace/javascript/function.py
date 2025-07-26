from __future__ import annotations

from functools import cached_property

from ..function import Function
from ..statement import BlockStatement, SimpleStatement, Statement
from . import language
from .statement import JavaScriptBlockStatement


class JavaScriptFunction(Function, JavaScriptBlockStatement):
    @cached_property
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(self._build_statements(self.body_node, self))

    def __find_next_nearest_stat(self, stat: Statement) -> Statement | None:
        stat_type = stat.node.type
        if stat_type == "return_statement":
            return None

        parent_statements = stat.parent.statements
        index = parent_statements.index(stat)
        if (
            index < len(parent_statements) - 1
            and parent_statements[index + 1].node.type != "else_clause"
        ):
            return parent_statements[index + 1]
        else:
            if isinstance(stat.parent, Function):
                return None
            assert isinstance(stat.parent, BlockStatement)
            if stat.parent.node.type in language.JAVASCRIPT.loop_statements:
                return stat.parent
            else:
                return self.__find_next_nearest_stat(stat.parent)

    def _build_post_cfg(self, statements: list[Statement]):
        for i in range(len(statements)):
            cur_stat = statements[i]
            type = cur_stat.node.type
            next_stat = self.__find_next_nearest_stat(cur_stat)
            next_stat = [next_stat] if next_stat is not None else []

            if isinstance(cur_stat, BlockStatement):
                child_statements = cur_stat.statements
                self._build_post_cfg(child_statements)
                if len(child_statements) > 0:
                    match type:
                        case "if_statement":
                            else_clause = cur_stat.statements_by_type("else_clause")
                            if len(else_clause) == 0:
                                cur_stat._post_control_statements = [
                                    child_statements[0]
                                ] + next_stat
                            else:
                                if len(child_statements) == 1:
                                    cur_stat._post_control_statements = list(
                                        set([else_clause[0]] + next_stat)
                                    )
                                else:
                                    cur_stat._post_control_statements = list(
                                        set([child_statements[0], else_clause[0]])
                                    )
                        case "else_clause":
                            cur_stat._post_control_statements = [child_statements[0]]
                        case _:
                            cur_stat._post_control_statements = [
                                child_statements[0]
                            ] + next_stat
                else:
                    cur_stat._post_control_statements = next_stat
            elif isinstance(cur_stat, SimpleStatement):
                match type:
                    case "continue_statement":
                        # search for the nearest loop statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.JAVASCRIPT.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            cur_stat._post_control_statements.append(loop_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case "break_statement":
                        # search for the nearest loop or switch statement
                        loop_stat = cur_stat
                        while (
                            loop_stat is not None
                            and loop_stat.node.type
                            not in language.JAVASCRIPT.loop_statements
                            and isinstance(loop_stat, Statement)
                        ):
                            loop_stat = loop_stat.parent
                        if loop_stat is not None:
                            assert isinstance(loop_stat, BlockStatement)
                            next_loop_stat = self.__find_next_nearest_stat(loop_stat)
                            cur_stat._post_control_statements = (
                                [next_loop_stat] if next_loop_stat else []
                            )
                        else:
                            cur_stat._post_control_statements = next_stat
                    case _:
                        cur_stat._post_control_statements = next_stat
