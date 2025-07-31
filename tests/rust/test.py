import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    project = scubatrace.Project.create(".", scubatrace.language.RUST)
    file = project.files["test.rs"]
    file.export_cfg_dot("test.dot")


if __name__ == "__main__":
    test_cfg()
