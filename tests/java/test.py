import sys

sys.path.append("../../")

import scubatrace


def testCFG():
    proj = scubatrace.Project.create(".", scubatrace.language.JAVA)
    test = proj.files["Test.java"]
    for func in test.functions:
        print(f"Function: {func.name}")
        func.export_cfg_dot(f"{func.name}_cfg.dot", with_ddg=False, with_cdg=True)
        print(f"CFG exported for function {func.name} to {func.name}_cfg.dot")


if __name__ == "__main__":
    testCFG()
