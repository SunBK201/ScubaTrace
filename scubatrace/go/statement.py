from __future__ import annotations

from functools import cached_property

from ..statement import BlockStatement, SimpleStatement, Statement


class GoSimpleStatement(SimpleStatement):
    @cached_property
    def post_controls(self) -> list[Statement]:
        if self.node_type in self.language.EXIT_STATEMENTS:
            return []
        exits_statements = self.function.exits if self.function is not None else []

        last_defer_statement = []
        from .function import GoFunction

        if self.function is not None and isinstance(self.function, GoFunction):
            last_defer_statement = (
                self.function.defer_statements[-1:]
                if len(self.function.defer_statements) > 0
                else []
            )

        if self.node_type == "defer_statement":
            assert isinstance(self.function, GoFunction)
            defter_index = self.function.defer_statements.index(self)
            return (
                [self.function.defer_statements[defter_index - 1]]
                if defter_index > 0
                else exits_statements
            )

        if self.node_type in self.language.CONTINUE_STATEMENTS:
            loop_stat = self.ancestor_by_types(self.language.LOOP_STATEMENTS)
            return [loop_stat] if loop_stat else []
        if self.node_type in self.language.BREAK_STATEMENTS:
            loop_stat = self.ancestor_by_types(
                self.language.LOOP_STATEMENTS + self.language.SWITCH_STATEMENTS
            )
            preorder_successor = loop_stat.preorder_successor if loop_stat else None
            return [preorder_successor] if preorder_successor else []
        if self.node_type in self.language.GOTO_STATEMENTS:
            function = self.function
            if function is not None:
                label_name_node = self.node.child_by_field_name("label")
                assert label_name_node is not None and label_name_node.text is not None
                label_name = label_name_node.text.decode()
                label_stat = function.query_oneshot(
                    self.language.query_goto_label(label_name)
                )
                return [label_stat] if label_stat else []

        if self.parent.node_type in self.language.LOOP_STATEMENTS:
            # while () {last_statement;}
            loop_stat = self.ancestor_by_types(self.language.LOOP_STATEMENTS)
            is_last_statement = self.next_sibling is None
            if is_last_statement:
                return [loop_stat] if loop_stat else []
        if self.parent.node_type in self.language.IF_STATEMENTS:
            # if () {last_statement;} else { ...}
            consequences = self.parent.statements_by_field_name("consequence")
            if self in consequences:
                is_last_consequences = consequences.index(self) == len(consequences) - 1
                if is_last_consequences:
                    return (
                        [self.right_uncle_ancestor] if self.right_uncle_ancestor else []
                    )

        preorder_successor = self.preorder_successor
        while (
            preorder_successor is not None
            and preorder_successor.node_type == "defer_statement"
        ):
            preorder_successor = preorder_successor.preorder_successor
        if preorder_successor is None:
            return last_defer_statement
        if preorder_successor.node_type in self.language.EXIT_STATEMENTS:
            return last_defer_statement
        else:
            return [preorder_successor]


class GoBlockStatement(BlockStatement):
    @cached_property
    def post_controls(self) -> list[Statement]:
        exits_statements = self.function.exits if self.function is not None else []
        last_defer_statement = []
        from .function import GoFunction

        if self.function is not None and isinstance(self.function, GoFunction):
            last_defer_statement = (
                self.function.defer_statements[-1:]
                if len(self.function.defer_statements) > 0
                else []
            )

        if self.node_type in self.language.IF_STATEMENTS:
            consequences = self.statements_by_field_name("consequence")
            alternatives = self.statements_by_field_name("alternative")
            nexts = []
            if len(consequences) > 0:
                nexts.append(consequences[0])
            if len(alternatives) > 0:
                nexts.append(alternatives[0])
            elif (
                self.preorder_successor is not None
                and self.preorder_successor not in exits_statements
            ):
                nexts.append(self.preorder_successor)
            else:
                nexts.extend(last_defer_statement)
            return nexts
        if self.node_type in self.language.SWITCH_STATEMENTS:
            if len(self.statements) > 0:
                return [self.statements[0]]
        if self.parent.node_type in self.language.SWITCH_STATEMENTS:
            if self.text.strip().startswith("default:") and len(self.statements) > 0:
                return [self.statements[0]]
        if self.parent.node_type in self.language.LOOP_STATEMENTS:
            # while () {last_statement;}
            loop_stat = self.ancestor_by_types(self.language.LOOP_STATEMENTS)
            is_last_statement = self.next_sibling is None
            if is_last_statement:
                return [loop_stat] if loop_stat else []

        nexts = [self.statements[0]] if len(self.statements) > 0 else []
        if self.preorder_successor is not None:
            nexts.append(self.preorder_successor)

        if len(last_defer_statement) > 0:
            nexts = [stat for stat in nexts if stat not in exits_statements]
            if len(nexts) == 0:
                return last_defer_statement
        return nexts
