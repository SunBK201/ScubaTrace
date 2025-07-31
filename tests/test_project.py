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

    def test_project_create(self):
        self.assertIsNotNone(self.project)
        self.assertEqual(self.project.language, scubatrace.language.C)
        self.assertEqual(self.project.path, str(self.project_path))
        self.assertTrue(Path(self.project.path).exists())

    def test_project_parser(self):
        parser = self.project.parser
        self.assertIsNotNone(parser)

    def test_project_files(self):
        files = self.project.files
        self.assertGreater(len(files), 0)
        for _, file in files.items():
            self.assertIsNotNone(file.name)

    def test_project_functions(self):
        functions = self.project.functions
        self.assertGreater(len(functions), 0)
        for func in functions:
            self.assertIsNotNone(func.name)

    def test_project_callgraph(self):
        callgraph = self.project.callgraph
        self.assertIsNotNone(callgraph)
        self.assertGreater(len(callgraph.nodes), 0)
        self.assertGreater(len(callgraph.edges), 0)
