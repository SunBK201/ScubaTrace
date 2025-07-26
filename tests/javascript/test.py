import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    project = scubatrace.Project.Project(".", scubatrace.language.JAVASCRIPT)
    for file in project.files.values():
        for function in file.functions:
            function.export_cfg_dot("test.dot", with_cdg=True, with_ddg=True)


if __name__ == "__main__":
    test_cfg()
