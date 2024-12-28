import sys

sys.path.append("..")

import scubatrace
from scubatrace.statement import CBlockStatement, CSimpleStatement


def main():
    a_proj = scubatrace.CProject("../tests")
    print(a_proj.files)


def testImports():
    a_proj = scubatrace.CProject("../tests")
    for file_path in a_proj.files:
        print(file_path)
        print(a_proj.files[file_path].imports)


def testAccessiableFunc():
    a_proj = scubatrace.CProject("../tests")
    for file_path in a_proj.files:
        file = a_proj.files[file_path]
        for func in file.functions:
            for access in func.accessible_functions:
                print(access.name)
        break


def testIsSimpleStatement():
    a_proj = scubatrace.CProject("../tests")
    for file_path in a_proj.files:
        file = a_proj.files[file_path]
        print(file_path)
        for func in file.functions:
            stmts = func.statements
            i = 0
            while stmts:
                temp_stmts = []
                i += 1
                for stmt in stmts:
                    if isinstance(stmt, CSimpleStatement):
                        print(f"{i} layer simple statments: {stmt.text}")
                    elif isinstance(stmt, CBlockStatement):
                        temp_stmts.extend(stmt.statements)
                        print(f"{i} layer block statements: {stmt.text}")

                stmts = temp_stmts


def testPreControl():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    # print(func_main.statements[3].pre_controls[2].text)
    func_main.export_cfg_dot("test.dot", with_cdg=True)


def testPreControlDep():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    print(func_main.statements[3].pre_control_dependents[0].text)


def testCallees():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    for func_main in test_c.functions:
        print(func_main.name, func_main.callees, func_main.callers)


if __name__ == "__main__":
    testPreControlDep()
