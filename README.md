# ScubaTrace
[![PyPI](https://img.shields.io/pypi/v/ScubaTrace?style=flat&logo=pypi&label=PyPI)](https://pypi.org/project/scubatrace/)
[![Docs](https://img.shields.io/github/deployments/SunBK201/ScubaTrace/github-pages?logo=sphinx&label=Docs)](https://sunbk201.github.io/ScubaTrace/)
[![CodeQL](https://github.com/SunBK201/ScubaTrace/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/SunBK201/ScubaTrace/actions/workflows/github-code-scanning/codeql)
[![License](https://img.shields.io/github/license/SunBK201/ScubaTrace)](https://github.com/SunBK201/ScubaTrace/blob/master/LICENSE)

Source level code analysis toolkit.

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
| Python     | Pyright                    | tree-sitter-python     | High     |
| JavaScript | typescript-language-server | tree-sitter-javascript | Medium   |
| Go         | gopls                      | tree-sitter-go         | Medium   |
| Rust       | Rust Analyzer              | tree-sitter-rust       | Medium   |
| Ruby       | Solargraph                 | tree-sitter-ruby       | Low      |
| Swift      | SourceKit-LSP              | tree-sitter-swift      | Low      |
| C#         | OmniSharp                  | tree-sitter-c-sharp    | Low      |
| PHP        | phpactor                   | tree-sitter-php        | Low      |

# Usage

```python
import scubatrace

# Initialize a ScubaTrace Project
# language can be set to one of the following:
# scubatrace.language.[C, JAVA, PYTHON, JAVASCRIPT, GO, RUST, RUBY, PHP, CSHARP, SWIFT]
project = scubatrace.Project.create("path/to/your/codebase", language=scubatrace.language.C)

# Get a file from the project
file = project.files["relative/path/to/your/file.c"]

# Get a function from the file
function = file.functions[0]
print(f"Function Name: {function.name}")
print(f"Source Code: {function.text}")

# Get the function's callers and print their names and callsites
callers = function.callers
for caller, callsites in callers.items():
    print(f"Caller: {caller.name}")
    for callsite in callsites:
        print(f"  Callsite: {callsite.text}")

# Get the first statement in file line
statement = file.statements_by_line(10)[0]

# Find the pre/post statements in control flow
pre_statements_in_control_flow = statement.pre_controls
post_statements_in_control_flow = statement.post_controls

# Get the first variable in statement
variable = statement.variables[0]
print(f"Variable: {variable.name}")

# Find the definitions/references of a variable
definitions = variable.definitions
references = variable.references

# Find the pre/post data dependencies of a variable
pre_data_dependencies = variable.pre_data_dependents
post_data_dependencies = variable.post_data_dependents

# Perform slicing in a function based on specified lines
# Configure the slicing with control depth and data-dependent depth
sliced_statements = function.slice_by_lines(
    lines=[10, 12, 18], control_depth=5, data_dependent_depth=8
)

# Get tree-sitter node in a file/function/statement
file_node = file.node
function_node = function.node
statement_node = statement.node
```

For more detailed information, refer to the [Documentation](https://sunbk201.github.io/ScubaTrace/).
