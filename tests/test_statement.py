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
