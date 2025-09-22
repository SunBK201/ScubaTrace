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
        self.file = self.project.files.get("car.cpp") or self.fail()
        self.clazz = self.file.classes_by_name("Car")[0]

    def test_class_create(self):
        clazz = scubatrace.Class.create(
            self.clazz.node,
            self.file,
        )
        self.assertIsNotNone(clazz)

    def test_class_functions(self):
        functions = self.clazz.functions
        self.assertEqual(len(functions), 3)
        function_names = sorted([func.name for func in functions])
        self.assertEqual(function_names, ["Car", "startEngine", "stopEngine"])
