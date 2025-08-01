import unittest
from pathlib import Path

import scubatrace


class TestIdentifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "c"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.C
        )
        self.file = self.project.files.get("main.c")
        assert self.file is not None
        self.assertGreater(len(self.file.statements), 0)
        self.statement = self.file.statements_by_line(14)[0]
        self.assertGreater(len(self.statement.identifiers), 0)
        self.identifier = self.statement.identifiers[0]

    def test_identifier_create(self):
        identifier = scubatrace.Identifier(self.identifier.node, self.statement)
        self.assertIsNotNone(identifier)
