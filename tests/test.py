import sys

sys.path.append("..")

import scubatrace
from scubatrace.parser import c_parser
from scubatrace.statement import CBlockStatement


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
            for stmt in func.statements:
                # print(stmt.text)
                if c_parser.is_simple_statement(stmt.node):
                    print("Simple Statement", stmt.text)
                    continue
                elif c_parser.is_block_statement(stmt.node):
                    print("block statements", stmt.text)
                    if isinstance(stmt, CBlockStatement):
                        for s in stmt.statements:
                            if isinstance(s, CBlockStatement):
                                print("first layer block statements", s.text)
                                for ss in s.statements:
                                    if isinstance(ss, CBlockStatement):
                                        for sss in ss.statements:
                                            print(
                                                "third layer block statements", sss.text
                                            )
                                        print("second layer block statements", ss.text)
                                    else:
                                        print("second layer simple statements", ss.text)

                    continue
                else:
                    print(stmt.text, stmt.node.type)


if __name__ == "__main__":
    testIsSimpleStatement()
