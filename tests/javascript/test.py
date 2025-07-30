import sys

sys.path.append("../../")

import scubatrace


def test_cfg():
    project = scubatrace.Project.create(".", scubatrace.language.JAVASCRIPT)
    for file in project.files.values():
        file.export_cfg_dot(f"{file.relpath}.dot")


def testImports():
    project = scubatrace.Project.create(".", scubatrace.language.JAVASCRIPT)
    test = project.files["test.js"]
    imports = test.imports
    for import_file in imports:
        print(f"Import: {import_file.relpath}")


if __name__ == "__main__":
    testImports()
