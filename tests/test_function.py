import unittest
from pathlib import Path

import scubatrace


class TestFunction(unittest.TestCase):
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
        function = self.file.function_by_line(11)
        assert function is not None
        self.function = function

    def test_function_create(self):
        function = scubatrace.Function.create(self.function.node, self.function.parent)
        self.assertIsNotNone(function)

    def test_function_callees(self):
        callees = self.function.callees
        self.assertGreater(len(callees), 0)
        self.assertIn("sub", [callee.name for callee in callees])
        self.assertIn("add", [callee.name for callee in callees])
        self.assertIn("printf", [callee.name for callee in callees])

    def test_function_callers(self):
        function = self.file.function_by_line(4)
        self.assertIsNotNone(function)
        assert function is not None
        callers = function.callers
        self.assertGreater(len(callers), 0)
        self.assertIn("main", [caller.name for caller in callers])

    def test_function_lines(self):
        self.assertGreater(len(self.function.lines), 0)

    def test_function_parameter_lines(self):
        self.assertEqual(len(self.function.parameter_lines), 1)
        self.assertEqual(self.function.parameter_lines[0], 9)

    def test_function_parameters(self):
        parameters = self.function.parameters
        self.assertEqual(parameters[0].text, "argc")
        self.assertEqual(parameters[1].text, "argv")

    def test_function_variables(self):
        variables = self.function.variables
        self.assertGreater(len(variables), 0)
        self.assertEqual(variables[0].text, "argc")
        self.assertEqual(variables[1].text, "argv")
        self.assertEqual(variables[len(variables) - 1].text, "count")

    def test_function_export_cfg_dot(self):
        cfg = self.function.export_cfg_dot("cfg.dot", with_cdg=True, with_ddg=True)
        self.assertIsNotNone(cfg)

    def test_function_slicing_by_lines(self):
        stats = self.function.slice_by_lines([14])
        self.assertEqual(stats[0].start_line, 9)
        self.assertEqual(stats[len(stats) - 1].start_line, 38)
