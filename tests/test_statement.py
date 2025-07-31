import unittest
from pathlib import Path

import scubatrace


class TestProject(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "c"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.C
        )
        self.file = self.project.files.get("main.c")
        assert self.file is not None
        self.function = self.file.function_by_line(11)
        assert self.function is not None
        statement = self.function.statements_by_line(14)
        assert statement is not None and len(statement) == 1
        self.statement = statement[0]

    def test_statement_create(self):
        statement = scubatrace.SimpleStatement.create(
            self.statement.node, self.statement.parent
        )
        self.assertIsNotNone(statement)
