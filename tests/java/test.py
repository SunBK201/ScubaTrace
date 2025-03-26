import sys

sys.path.append("../../")

import scubatrace
from scubatrace.file import JavaFile


def main():
    a_proj = scubatrace.JavaProject("../java")
    test = a_proj.files["Test.java"]
    clazz = test.classes[0]
    for method in clazz.methods:
        if method.name == "countRearrangedNumbers":
            method.export_cfg_dot("test.dot", with_ddg=True)
        


if __name__ == "__main__":
    main()
