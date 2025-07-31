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

    def test_function_create(self):
        assert self.function is not None
        function = scubatrace.Function.create(self.function.node, self.function.parent)
        self.assertIsNotNone(function)
