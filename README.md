# ScubaTrace

Source Level Code Analysis Toolkit.

<br>
<img src="https://sunbk201.oss-cn-beijing.aliyuncs.com/img/ScubaTrace.png" width="61.8%">

ScubaTrace is a code analysis toolkit that leverages tree-sitter and LSP (Language Server Protocol) to provide parsing, analysis, and context extraction capabilities for multiple programming languages.

Unlike most traditional static analysis tools that rely on compilation to extract Intermediate Representation (IR) for code analysis, ScubaTrace delivers analysis capabilities even when code repositories are incomplete or unable to compile. This resilience makes it particularly valuable for scenarios where traditional analysis approaches would fail, enabling developers and security researchers to gain insights from code that might otherwise be inaccessible to conventional static analysis methodologies.

ScubaTrace serves as a portable analysis solution for IDE development, AI-powered coding tools, and SAST (Static Application Security Testing).

# Features

- **Multi-Language Support**
- **No Need To Compile**
- **Statement-Based AST Abstraction**
- **Call Graph**
- **Control Flow Graph**
- **Data/Control Dependency Graph**
- **References Inference**
- **CPG Based Multi-Granularity Slicing**
- **Built on Tree-sitter and LSP**

# Install

```bash
pip install scubatrace
```

> [!NOTE]
> If you encounter a `pygraphviz` installation failure during `pip install`, you need to install the Graphviz development package. You can install it using the following command:
>
> ```bash
> # For Debian/Ubuntu
> apt install libgraphviz-dev
> # For macOS, Ref: https://pygraphviz.github.io/documentation/stable/install.html#homebrew
> brew install graphviz
> ```

# Supported Languages

ScubaTrace supports multiple programming languages, including:

| Language   | Language Server            | Tree-sitter Parser     | Maturity |
| ---------- | -------------------------- | ---------------------- | -------- |
| C/C++      | clangd                     | tree-sitter-cpp        | High     |
| Java       | Eclipse JDT LS             | tree-sitter-java       | High     |
| Python     | pylsp                      | tree-sitter-python     | High     |
| JavaScript | typescript-language-server | tree-sitter-javascript | High     |
| Go         | gopls                      | tree-sitter-go         | WIP      |
| Rust       | Rust Analyzer              | tree-sitter-rust       | WIP      |
| Ruby       | Solargraph                 | tree-sitter-ruby       | WIP      |
| Swift      | SourceKit-LSP              | tree-sitter-swift      | WIP      |
| C#         | OmniSharp                  | tree-sitter-c-sharp    | WIP      |
| PHP        | phpactor                   | tree-sitter-php        | WIP      |

# Usage

## Project-Level Analysis

### Load a project (codebase)

```py
proj = scubatrace.CProject("path/to/your/codebase", enable_lsp=True)
```

### Call Graph

```py
# Get the call graph of the project
callgraph = proj.callgraph
# Export call graph to a dot file
proj.export_callgraph("callgraph.dot")
```

### Code Search

```py
stat = proj.search_function("relative/path/to/your/file.c", start_line=20)
```

## File-Level Analysis

### Load a file from a project

```py
file = proj.files["relative/path/to/your/file.c"]
```

## Function-Level Analysis

### Load a function from a file

```py
the_first_func = file.functions[0]
func_in_tenth_line = file.function_by_line(10)
```

### Call Relationships

```py
def callers(self) -> dict[Function, list[Statement]]: ...
def callees(self) -> dict[Function, list[Statement]]: ...
def calls(self) -> list[Statement]: ...
```

### Function Control Flow Graph

```py
# Export the control flow graph to a dot file
func.export_cfg_dot("cfg.dot")
```

### Function Data Dependency Graph

```py
# Export the data dependency graph to a dot file
func.export_cfg_dot("ddg.dot", with_ddg=True)
```

### Function Control Dependency Graph

```py
# Export the control dependency graph to a dot file
func.export_cfg_dot("cdg.dot", with_cdg=True)
```

### Function Code Walk

```py
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
```

### Multi-Granularity Slicing

```py
# Slicing by lines
lines_you_interest = [4, 5, 19]
slice_statements = func.slice_by_lines(
    lines=lines_you_interest,
    control_depth=3,
    data_dependent_depth=5,
    control_dependent_depth=2,
)

# Slicing by statements
statements_you_interest = func.statements[0:3]
slice_statements = func.slice_by_statements(
    statements=statements_you_interest,
    control_depth=3,
    data_dependent_depth=5,
    control_dependent_depth=2,
)
```

## Statement-Level Analysis

### Load a statement from a function

```py
the_first_stmt = the_first_func.statements[0]
stmt_in_second_line = the_first_func.statement_by_line(2)
stmt_by_type = func.statements_by_type('tree-sitter Queries', recursive=True)
```

### Statement Controls

```
pre_controls: list[Statement] = stat.pre_controls
post_controls: list[Statement] = stat.post_controls
```

### Statement Data Dependencies

```py
pre_data_dependents: dict[Identifier, list[Statement]] = stat.pre_data_dependents
post_data_dependents: dict[Identifier, list[Statement]] = stat.post_data_dependents
```

### Statement Control Dependencies

```py
pre_control_dependents: list[Statement] = stat.pre_control_dependents
post_control_dependents: list[Statement] = stat.post_control_dependents
```

### Statement References

```py
references: dict[Identifier, list[Statement]] = stat.references
```

### Statement Definitions

```py
definitions: dict[Identifier, list[Statement]] = stat.definitions
```

### Taint Analysis

```py
# Check if the statement is tainted from function entry
is_taint_from_entry: bool = stat.is_taint_from_entry
```

## AST Node

You can also get the AST node from a file, function, or statement.

```py
file_ast = file.node
func_ast = func.node
stmt_ast = stat.node
```
