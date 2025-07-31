import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    a_proj = scubatrace.Project.create(".", language=scubatrace.language.GO)
    main = a_proj.files["main.go"]
    main.export_cfg_dot("test.dot")

if __name__ == "__main__":
    test_cfg()
