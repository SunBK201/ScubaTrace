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

    def test_file_imports(self):
        assert self.file is not None
        imports = self.file.imports
        self.assertGreater(len(imports), 0)
        for imp in imports:
            self.assertIsNotNone(imp.name)

    def test_file_functions(self):
        assert self.file is not None
        functions = self.file.functions
        self.assertGreater(len(functions), 0)
        for func in functions:
            self.assertIsNotNone(func.name)

    def test_file_statements(self):
        assert self.file is not None
        statements = self.file.statements
        self.assertGreater(len(statements), 0)
        for stmt in statements:
            self.assertIsNotNone(stmt.text)

    def test_file_variables(self):
        assert self.file is not None
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
