import sys

sys.path.append("../../")

import time

import scubatrace
from scubatrace.cpp.file import CFile
from scubatrace.statement import BlockStatement, SimpleStatement


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
                    if isinstance(stmt, SimpleStatement):
                        print(f"{i} layer simple statments: {stmt.text}")
                    elif isinstance(stmt, BlockStatement):
                        temp_stmts.extend(stmt.statements)
                        print(f"{i} layer block statements: {stmt.text}")

                stmts = temp_stmts


def testPreControl():
    a_proj = scubatrace.CProject("../c")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    # print(func_main.statements[3].pre_controls[2].text)
    func_main.export_cfg_dot("test.dot", with_cdg=True, with_ddg=True)


def testPostControl():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[0]
    print(func_main.statements[0].pre_data_dependents)


def testPreControlDep():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    print(func_main.statements[3].pre_control_dependents[0].text)


def testImports():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    imports = test_c.imports
    for import_file in imports:
        print(f"Import: {import_file.relpath}")


def testSourceHeader():
    a_proj = scubatrace.CProject(".")
    for file_path in a_proj.files:
        file = a_proj.files[file_path]
        if not isinstance(file, CFile):
            continue
        source_header = file.source_header
        if source_header:
            print(f"Source header for {file.relpath}: {source_header.relpath}")
        else:
            print(f"No source header found for {file.relpath}")


def testCalls():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    calls = func_main.calls
    for call in calls:
        print(f"Call: {call.text} (Line {call.start_line})")
        print(f"  Function: {call.function}")
        print(f"  File: {call.file.relpath}")
        print(f"  Start Line: {call.start_line}, End Line: {call.end_line}")


def testCallees():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    for func in test_c.functions:
        print(f"Function: {func.name}")
        callees = func.callees
        for callee_func, statements in callees.items():
            print(f"  Callee: {callee_func.name}, Signature: {callee_func.signature}")
            for stat in statements:
                print(f"    Statement: {stat.text} (Line {stat.start_line})")


def testCallers():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    for func in test_c.functions:
        print(f"Function: {func.name}")
        callers = func.callers
        for caller_func, statements in callers.items():
            print(f"  Caller: {caller_func.name}, Signature: {caller_func.signature}")
            for stat in statements:
                print(f"    Statement: {stat.text} (Line {stat.start_line})")


def testIdentifiers():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    for func in test_c.functions:
        print(func.name)
        for stmt in func.statements:
            for id in stmt.identifiers:
                print(id.text, id.signature)


def testReferences():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    stat = func_main.statements[5]
    print(stat)
    print(stat.identifiers[0])
    for ref in stat.identifiers[0].references:
        print(ref)


def testPreDataDependency():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    line = 29
    func = test_c.function_by_line(line)
    assert func is not None, f"Function not found at line {line}"
    for stat in func.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        for var, stats in stat.pre_data_dependents.items():
            print(f"  Variable: {var.text}")
            for s in stats:
                print(
                    f"    Pre Data Dependent Statement: {s.text} (Line {s.start_line})"
                )


def testPostDataDependency():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    stat = func_main.statements[3]
    print(f"statement: {stat.text}")
    for var, stat in stat.post_data_dependents.items():
        print(f"variable: {var}")
        for s in stat:
            print(f"statement: {s.text}")


def testPDG():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    # print(func_main.statements[3].pre_controls[2].text)
    func_main.export_cfg_dot("test.dot", with_ddg=True, with_cdg=True)


def test_slice_by_statements():
    a_proj = scubatrace.CProject("../tests")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    slice_criteria = [func_main.statements[4]]
    for stat in slice_criteria:
        print("slice criteria: ", stat.text)
    stats = func_main.slice_by_statements(
        slice_criteria,
        control_depth=1,
        data_dependent_depth=1,
        control_dependent_depth=0,
    )
    for stat in stats:
        print(stat.text)


def test_slice_by_lines():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["engine.cpp"]
    func_main = test_c.function_by_line(181)
    assert func_main is not None, "Function not found at line 181"
    slice_criteria = [2542]
    for line in slice_criteria:
        print("slice criteria: ", line)
    stats = func_main.slice_by_lines(
        slice_criteria,
        control_depth=3,
        data_dependent_depth=3,
        control_dependent_depth=2,
    )
    for stat in stats:
        print(stat.text)


def test_cg():
    start_time = time.time()
    a_proj = scubatrace.CProject("/Users/sunbk201/Downloads/marco_expanded_repo")
    a_proj.export_callgraph(".")
    end_time = time.time()
    print(f"Time: {end_time - start_time:.2f} s")


def test_statements_by_line():
    a_proj = scubatrace.CProject(".")
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    for line in range(7, 20):
        statements = func_main.statements_by_line(line)
        if statements:
            print(f"Line {line}:")
            for stat in statements:
                print(f"  {stat.text}")
        else:
            print(f"Line {line}: No statements found.")


def test_statement_definitions():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    defs = func_main.statements[5].definitions
    for var, statements in defs.items():
        print(f"Variable: {var.text}")
        for statement in statements:
            print(f"  Defined at: {statement.text} (Line {statement.start_line})")


def test_statement_references():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    line = 562
    func_main = test_c.function_by_line(line)
    assert func_main is not None, f"Function not found at line {line}"
    for stat in func_main.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        statement_refs = stat.references
        if statement_refs:
            for identifier, refs in statement_refs.items():
                print(
                    f"  Identifier: {identifier.text} (Signature: {identifier.signature})"
                )
                for ref in refs:
                    print(
                        f"    Reference: {ref.text} (Line {ref.start_line}, File: {ref.file.relpath})"
                    )
        else:
            print("  No references found.")


def test_is_taint_from_entry():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    print(func_main.statements[5].is_taint_from_entry)


def test_identifiers_is_taint_from_entry():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    func_main = test_c.functions[1]
    for stat in func_main.statements:
        print(f"Statement: {stat.text}")
        for variables in stat.variables:
            print(
                f"  Identifier: {variables.text}, is_taint_from_entry: {variables.is_taint_from_entry}"
            )


def test_file_statements_by_line():
    a_proj = scubatrace.CProject(".", enable_lsp=False)
    test_c = a_proj.files["test.c"]
    line = 3
    statements = test_c.statements_by_line(line)
    for stat in statements:
        print(f"Line {line}: {stat.text} (File: {test_c.relpath})")


def test_identifiers_references():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    func_line = 562
    func = test_c.function_by_line(func_line)
    if func is None:
        print(f"No function found at line {func_line}")
        return
    for stat in func.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        for identifier in stat.variables:
            print(
                f"  Identifier: {identifier.text} (Signature: {identifier.signature})"
            )
            references = identifier.references
            if references:
                for ref in references:
                    print(
                        f"    Reference: {ref.text} (Line {ref.start_line}, File: {ref.file.relpath})"
                    )
            else:
                print("    No references found.")


def test_identifiers_definitions():
    a_proj = scubatrace.CProject(".", enable_lsp=True)
    test_c = a_proj.files["test.c"]
    line = 29
    stats = test_c.statements_by_line(line)
    for stat in stats:
        print(f"Statement: {stat.text} (Line {line})")
        for identifier in stat.identifiers:
            print(f"  Identifier: {identifier.text}")
            defs = identifier.definitions
            if defs:
                for def_stat in defs:
                    print(
                        f"    Defined at: {def_stat.text} (Line {def_stat.start_line})"
                    )
            else:
                print("    No definitions found.")


def test_statement_identifiers():
    project = scubatrace.CProject(".", enable_lsp=True)
    test_c = project.files["test.c"]
    func_main = test_c.functions[1]
    for stat in func_main.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        for identifier in stat.identifiers:
            print(
                f"  Identifier: {identifier.text} (Signature: {identifier.signature})"
            )


def test_identifier_pre_data_dependents():
    project = scubatrace.CProject(".", enable_lsp=True)
    test_c = project.files["test.c"]
    func_main = test_c.functions[2]
    for stat in func_main.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        for identifier in stat.identifiers:
            print(
                f"  Identifier: {identifier.text} (Signature: {identifier.signature})"
            )
            pre_data_dependents = identifier.pre_data_dependents
            if pre_data_dependents:
                for dep in pre_data_dependents:
                    print(
                        f"    Pre Data Dependent: {dep.text}, (Line {dep.start_line})"
                    )
            else:
                print("    No pre data dependent found.")


def test_identifier_post_data_dependents():
    project = scubatrace.Project.Project(".", language.C)
    test_c = project.files["test.c"]
    func_main = test_c.functions[1]
    for stat in func_main.statements:
        print(f"Statement: {stat.text} (Line {stat.start_line})")
        for identifier in stat.identifiers:
            print(
                f"  Identifier: {identifier.text} (Signature: {identifier.signature})"
            )
            post_data_dependents = identifier.post_data_dependents
            if post_data_dependents:
                for dep in post_data_dependents:
                    print(
                        f"    Post Data Dependent: {dep.text}, (Line {dep.start_line})"
                    )
            else:
                print("    No post data dependent found.")


if __name__ == "__main__":
    testCalls()
