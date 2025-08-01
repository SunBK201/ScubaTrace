import unittest
from pathlib import Path

import scubatrace


class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "c"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.C
        )
        file = self.project.files.get("main.c")
        assert file is not None
        self.file = file

    def test_file_create(self):
        file = scubatrace.File.create(
            str(self.project_path / "main.c"),
            self.project,
        )
        self.assertIsNotNone(file)

    def test_file_imports(self):
        imports = self.file.imports
        self.assertGreater(len(imports), 0)
        for imp in imports:
            self.assertTrue(imp.name in ["stdio.h", "sub.h"])

    def test_file_functions(self):
        functions = self.file.functions
        self.assertGreater(len(functions), 0)
        for func in functions:
            self.assertIsNotNone(func.name)

    def test_file_function_by_line(self):
        function = self.file.function_by_line(5)
        self.assertIsNotNone(function)
        assert function is not None
        self.assertEqual(function.name, "add")

    def test_file_statements(self):
        statements = self.file.statements
        self.assertGreater(len(statements), 0)
        for stmt in statements:
            self.assertIsNotNone(stmt.text)

    def test_file_statement_by_line(self):
        statements = self.file.statements_by_line(14)
        self.assertGreater(len(statements), 0)
        self.assertEqual(statements[0].text, "int c = count + argc;")

        self.assertEqual(len(self.file.statements_by_line(-1)), 0)
        self.assertGreater(len(self.file.statements_by_line(1)), 0)

        self.assertEqual(self.file.statements_by_line(18)[0].text, "a -= 1;")

    def test_file_identifiers(self):
        identifiers = self.file.identifiers
        self.assertGreater(len(identifiers), 0)
        for identifier in identifiers:
            self.assertIsNotNone(identifier.name)

    def test_file_variables(self):
        variables = self.file.variables
        self.assertGreater(len(variables), 0)
        for var in variables:
            self.assertIsNotNone(var.name)

    def test_file_cfg(self):
        assert self.file is not None
        cfg = self.file.export_cfg_dot(f"{self.file.name}.dot")
        self.assertIsNotNone(cfg)
        self.assertGreater(len(cfg.nodes), 0)
        self.assertGreater(len(cfg.edges), 0)

    def test_file_query(self):
        query_str = """
            (call_expression
                function: (identifier)@func
                (#eq? @func "sub")
            )@call
        """
        query = self.file.query(query_str)
        target_lines = [6, 36]
        self.assertEqual(len(query), len(target_lines))
        for stat in query:
            self.assertIn(stat.start_line, target_lines)

        one_shot_result = self.file.query_oneshot(query_str)
        self.assertIsNotNone(one_shot_result)
        assert one_shot_result is not None
        self.assertIn(one_shot_result.start_line, target_lines)
