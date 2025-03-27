import sys

sys.path.append("../../")

import scubatrace


def main():
    a_proj = scubatrace.PythonProject("../python")
    test = a_proj.files["test.py"]
    for method in test.functions:
        method.export_cfg_dot("test.dot", with_cdg=True, with_ddg=True)
        print(method.slice_by_statements([method.statements[0]]))


if __name__ == "__main__":
    main()
