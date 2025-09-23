import unittest
from pathlib import Path

import scubatrace


class TestClass(unittest.TestCase):
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

    def test_class_fields(self):
        fields = self.clazz.fields
        self.assertEqual(len(fields), 2)
        field_names = sorted([field.name for field in fields])
        self.assertEqual(field_names, ["brand", "color"])


class TestPythonClass(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "python"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.PYTHON
        )
        self.file = self.project.files.get("car.py") or self.fail()
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
        self.assertEqual(function_names, ["__init__", "start_engine", "stop_engine"])

    def test_class_fields(self):
        fields = self.clazz.fields
        self.assertEqual(len(fields), 2)
        field_names = sorted([field.name for field in fields])
        self.assertEqual(field_names, ["a", "b"])


class TestJavaClass(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.samples_dir = self.test_dir / "samples"
        self.project_path = self.samples_dir / "java"
        self.project = scubatrace.Project.create(
            str(self.project_path), language=scubatrace.language.JAVA, enable_lsp=False
        )
        self.file = self.project.files.get("Car.java") or self.fail()
        self.clazz = self.file.classes_by_name("Car")[0]

    def test_class_create(self):
        clazz = scubatrace.Class.create(
            self.clazz.node,
            self.file,
        )
        self.assertIsNotNone(clazz)

    def test_class_functions(self):
        functions = self.clazz.functions
        self.assertEqual(len(functions), 5)
        function_names = sorted([func.name for func in functions])
        self.assertEqual(
            function_names, ["Car", "getBrand", "getColor", "startEngine", "stopEngine"]
        )

    def test_class_fields(self):
        fields = self.clazz.fields
        self.assertEqual(len(fields), 2)
        field_names = sorted([field.name for field in fields])
        self.assertEqual(field_names, ["brand", "color"])
