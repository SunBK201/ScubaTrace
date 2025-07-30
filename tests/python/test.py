import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    project = scubatrace.PythonProject(".")
    file = project.files["test.py"]
    file.export_cfg_dot("test.dot")


if __name__ == "__main__":
    test_cfg()
