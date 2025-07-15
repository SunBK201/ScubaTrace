from identifier import Identifier
from statement import Statement

import scubatrace

codebase_path = "path/to/your/codebase"
proj = scubatrace.CProject(codebase_path)
proj.callgraph_joern
proj.export_callgraph("callgraph.dot")
proj.search_function("file/path/to/your/file.c", start_line=0)

file_path = "relative/path/to/your/file.c"
file = proj.files[file_path]

func = file.functions[0]
callers = func.callers
callfrom, callto, callsite_line, callsite_column = (
    callers[0].src,
    callers[0].dst,
    callers[0].line,
    callers[0].column,
)
callees = func.callees
callfrom, callto, callsite_line, callsite_column = (
    callees[0].src,
    callees[0].dst,
    callees[0].line,
    callees[0].column,
)

lines_you_interest = [4, 5, 19]
slice_statements = func.slice_by_lines(
    lines=lines_you_interest,
    control_depth=3,
    data_dependent_depth=5,
    control_dependent_depth=2,
)

statements_you_interest = func.statements[0:3]
slice_statements = func.slice_by_statements(
    statements=statements_you_interest,
    control_depth=3,
    data_dependent_depth=5,
    control_dependent_depth=2,
)


statements_you_interest = list(
    func.walk_backward(
        filter=lambda x: x.is_jump_statement,
        stop_by=lambda x: x.is_jump_statement,
        depth=-1,
        base="control",
    )
)

statements_you_interest = list(
    func.walk_forward(
        filter=lambda x: x.is_jump_statement,
        stop_by=lambda x: x.is_jump_statement,
        depth=-1,
        base="control",
    )
)

stat = func.statements[0]
pre_controls: list[Statement] = stat.pre_controls
post_controls: list[Statement] = stat.post_controls
pre_data_dependents: dict[Identifier, list[Statement]] = stat.pre_data_dependents
post_data_dependents: dict[Identifier, list[Statement]] = stat.post_data_dependents
pre_control_dependents: list[Statement] = stat.pre_control_dependents
post_control_dependents: list[Statement] = stat.post_control_dependents
