import sys
from html import parser

sys.path.append("..")

import scubatrace
from scubatrace.parser import c_parser


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
                    continue
                else:
                    print(stmt.text, stmt.node.type)


if __name__ == "__main__":
    testIsSimpleStatement()
