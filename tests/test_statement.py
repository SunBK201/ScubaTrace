import unittest
from pathlib import Path

import scubatrace


class TestStatement(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "c"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.C
        )
        self.file = self.project.files.get("main.c") or self.fail()
        self.function = self.file.function_by_line(11) or self.fail()
        statement = self.function.statements_by_line(14)
        self.statement = statement[0]

    def test_statement_create(self):
        statement = scubatrace.SimpleStatement.create(
            self.statement.node, self.statement.parent
        )
        self.assertIsNotNone(statement)

    def test_statement_lsp(self):
        lsp = self.statement.lsp
        self.assertIsNotNone(lsp)

    def test_statement_variables(self):
        variables = self.statement.variables
        self.assertGreater(len(variables), 0)

    def test_statement_statements(self):
        if isinstance(self.statement, scubatrace.BlockStatement):
            statements = self.statement.statements
            self.assertGreater(len(statements), 0)

    def test_statement_pre_data_dependents(self):
        dependents = self.statement.pre_data_dependents
        self.assertGreater(len(dependents), 0)

    def test_statement_post_data_dependents(self):
        dependents = self.statement.post_data_dependents
        self.assertGreater(len(dependents), 0)

    def test_statement_pre_controls(self):
        pre_controls = self.statement.pre_controls
        self.assertGreater(len(pre_controls), 0)

    def test_statement_post_controls(self):
        post_controls = self.statement.post_controls
        self.assertGreater(len(post_controls), 0)

    def test_statement_definitions(self):
        definitions = self.statement.definitions
        self.assertGreater(len(definitions), 0)

    def test_statement_references(self):
        references = self.statement.references
        self.assertGreater(len(references), 0)

    def test_statement_is_taint_from_entry(self):
        is_taint_from_entry = self.statement.is_taint_from_entry
        self.assertIsInstance(is_taint_from_entry, bool)


class TestJavaScriptStatement(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "javascript"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.JAVASCRIPT
        )
        self.file = self.project.files.get("index.js") or self.fail()
        statement = self.file.statements_by_line(4)
        self.statement = statement[0]

    def test_statement_create(self):
        statement = scubatrace.SimpleStatement.create(
            self.statement.node, self.statement.parent
        )
        self.assertIsNotNone(statement)

    def test_statement_walk_backward(self):
        for stmt in self.statement.walk_backward(depth=3, base="control"):
            self.assertIn(stmt.start_line, [1, 2, 3, 4])
