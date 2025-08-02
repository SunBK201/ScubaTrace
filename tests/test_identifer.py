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
        self.file = self.project.files.get("main.c") or self.fail()
        self.assertGreater(len(self.file.statements), 0)
        self.statement = self.file.statements_by_line(16)[0]
        self.assertGreater(len(self.statement.identifiers), 0)
        self.identifier = self.statement.identifiers[0]

    def test_identifier_create(self):
        identifier = scubatrace.Identifier(self.identifier.node, self.statement)
        self.assertIsNotNone(identifier)

    def test_identifier_post_data_dependents(self):
        dependents = self.identifier.post_data_dependents
        self.assertEqual(len(dependents), 5)
        dependents_lines = sorted([dep.start_line for dep in dependents])
        self.assertEqual(dependents_lines, [17, 17, 36, 38, 40])

    def test_identifier_type_info(self):
        identifier = self.file.identifier_by_position(59, 6) or self.fail()
        type_info = identifier.type_info
        self.assertEqual(type_info, "int *")

    def test_identifier_is_pointer(self):
        identifier = self.file.identifier_by_position(11, 27) or self.fail()
        self.assertTrue(identifier.is_pointer)
        identifier = self.file.identifier_by_position(59, 6) or self.fail()
        self.assertTrue(identifier.is_pointer)
        identifier = self.file.identifier_by_position(53, 5) or self.fail()
        self.assertFalse(identifier.is_pointer)

    def test_identifier_is_argument(self):
        self.assertFalse(self.identifier.is_argument)
        identifier = self.file.identifier_by_position(17, 26) or self.fail()
        self.assertTrue(identifier.is_argument)
        identifier = self.file.identifier_by_position(59, 6) or self.fail()
        self.assertFalse(identifier.is_argument)
        identifier = self.file.identifier_by_position(47, 41) or self.fail()
        self.assertTrue(identifier.is_argument)
