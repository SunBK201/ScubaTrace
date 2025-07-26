import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    a_proj = scubatrace.Project.Project(".", language=scubatrace.language.GO)
    main = a_proj.files["main.go"]
    for function in main.functions:
        function.export_cfg_dot("test.dot", with_cdg=True, with_ddg=True)


if __name__ == "__main__":
    test_cfg()
