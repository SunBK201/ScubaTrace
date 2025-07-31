import sys

sys.path.append("../../")

import scubatrace


def testCFG():
    proj = scubatrace.Project.create(".", scubatrace.language.JAVA)
    test = proj.files["Test.java"]
    test.export_cfg_dot("cfg.dot")


if __name__ == "__main__":
    testCFG()
