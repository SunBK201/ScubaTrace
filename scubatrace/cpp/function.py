from __future__ import annotations

from functools import cached_property

from tree_sitter import Node

from ..function import Function
from ..statement import BlockStatement, Statement
from . import language
from .statement import CBlockStatement, SimpleStatement


class CFunction(Function, CBlockStatement):
    @cached_property
    def name_node(self) -> Node:
        name_node = self.node.child_by_field_name("declarator")
        while name_node is not None and name_node.type not in {
            "identifier",
            "operator_name",
            "type_identifier",
        }:
            all_temp_name_node = name_node
            if (
                name_node.child_by_field_name("declarator") is None
                and name_node.type == "reference_declarator"
            ):
                for temp_node in name_node.children:
                    if temp_node.type == "function_declarator":
                        name_node = temp_node
                        break
            if name_node.child_by_field_name("declarator") is not None:
                name_node = name_node.child_by_field_name("declarator")
            # int *a()
            if (
                name_node is not None
                and name_node.type == "field_identifier"
                and name_node.child_by_field_name("declarator") is None
            ):
                break
            if name_node == all_temp_name_node:
                break
        assert name_node is not None
        return name_node

    @cached_property
    def parameter_lines(self) -> list[int]:
        declarator_node = self.node.child_by_field_name("declarator")
        if declarator_node is None:
            return [self.start_line]
        param_node = declarator_node.child_by_field_name("parameters")
        if param_node is None:
            return [self.start_line]
        param_node_start_line = param_node.start_point[0] + 1
        param_node_end_line = param_node.end_point[0] + 1
        return list(range(param_node_start_line, param_node_end_line + 1))

    @cached_property
    def statements(self) -> list[Statement]:
        if self.body_node is None:
            return []
        return list(self._build_statements(self.body_node, self))

    def __find_next_nearest_stat(
        self, stat: Statement, jump: int = 0
    ) -> Statement | None:
        stat_type = stat.node.type
        if stat_type == "return_statement":
            return None

        if jump == -1:
            jump = 0x3F3F3F
        while (
            jump > 0
            and stat.parent is not None
            and isinstance(stat.parent, BlockStatement)
        ):
            stat = stat.parent
            jump -= 1

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
            if stat.parent.node.type in language.C.loop_statements:
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
                            and loop_stat.node.type not in language.C.loop_statements
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
                            not in language.C.loop_statements + ["switch_statement"]
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
                    case "goto_statement":
                        goto_label = cur_stat.node.child_by_field_name("label")
                        assert goto_label is not None and goto_label.text is not None
                        label_name = goto_label.text.decode()
                        label_stat = None
                        for stat in self.statements_by_type(
                            "labeled_statement", recursive=True
                        ):
                            label_identifier_node = stat.node.child_by_field_name(
                                "label"
                            )
                            assert (
                                label_identifier_node is not None
                                and label_identifier_node.text is not None
                            )
                            label_identifier = label_identifier_node.text.decode()
                            if label_identifier == label_name:
                                label_stat = stat
                                break
                        if label_stat is not None:
                            cur_stat._post_control_statements.append(label_stat)
                        else:
                            cur_stat._post_control_statements = next_stat
                    case _:
                        cur_stat._post_control_statements = next_stat
