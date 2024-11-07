# ScubaTrace

![ScubaTrace](./docs/scubatrace.png "ScubaTrace")

# Usage

```py
import scubatrace
a_proj = scubatrace.CProject("../tests")
print(a_proj.files["src/test.c"].structs[0].name)
print(a_proj.files["src/test.c"].functions["foo"].name)
print(a_proj.files["src/test.c"].functions["foo"].calls)
print(a_proj.files["src/test.c"].functions["foo"].callee)
print(a_proj.files["src/test.c"].functions["foo"].caller)
print(a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].ref_statements)
print(a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].defination)
print(a_proj.dependencies)
print(a_proj.licences)
```

# Development

# Project

```python
def files(self) -> dict[str, File]:
def functions(self) -> list[Function]:
def classes(self) -> list[Function]:
def methods(self) -> list[Function]:
```

# File

```python
def abspath(self) -> str:
def relpath(self) -> str:
def text(self) -> str:

def imports(self) -> list[File]: ...
def accessible_files(self) -> list[File]: ...

def functions(self) -> list[Function]: ...
def functions(self) -> list[Function]: ...
```

# Function

```python
def text(self) -> str:
def start_line(self) -> int:
def end_line(self) -> int:
def length(self):
def lines(self) -> dict[int, str]:
def body_node(self) -> Node | None:
def body_start_line(self) -> int:
def body_end_line(self) -> int:
def name(self) -> str: ...

def accessible_functions(self) -> list[Function]: ...
def callees(self) -> list[Function]: ...
def callers(self) -> list[Function]: ...
def calls(self) -> dictlist[Statement]: ...
def statements(self) -> list[Statement]: ...
```

# Class

```python
def text(self) -> str:
def start_line(self) -> int:
def end_line(self) -> int:
def length(self):
def name(self) -> str: ...

def methods(self) -> list[Method]: ...
def fields(self) -> list[str]: ...
def parents(self) -> list[Class]
def children(self) -> list[Class]
```

# Method

```python
def name(self) -> str: ...
def text(self) -> str:
def start_line(self) -> int:
def end_line(self) -> int:
def length(self):
def lines(self) -> dict[int, str]:
def body_node(self) -> Node | None:
def body_start_line(self) -> int:
def body_end_line(self) -> int:
def name(self) -> str: ...

def accessible_functions(self) -> list[Function]: ...
def callees(self) -> list[Function]: ...
def callers(self) -> list[Function]: ...
def calls(self) -> list[Statement]: ...
def statements(self) -> list[Statement]: ...
```

# Statement

```python
def text(self) -> str:
def start_line(self) -> int:
def end_line(self) -> int:
def length(self) -> int:

def forward_controls(self) -> list[Statement]:
def backward_controls(self) -> list[Statement]:
def forward_datas(self, identifier: str) -> list[Statement]:
def backward_datas(self, identifier: str) -> list[Statement]:
```

# Patch(Commit)

```python
def message(self) -> str:
def author(self) -> str:
def commit_date(self) -> datetime:
def author_date(self) -> datetime:
def next_commit(self) -> Commit:
def pre_commmit(self) -> Commit:

def added_files(self) -> list[File]:
def deleted_files(self) -> list[File]:

def added_imports(self) -> list[Import]:
def deleted_imports(self) -> list[Import]:

def added_classes(self) -> list[Class]:
def deleted_classes(self) -> list[Class]:

def added_methods(self) -> list[Method]:
def changed_methods(self) -> list[Method]:
def deleted_methods(self) -> list[Method]:

def added_fields(self) -> list[Field]:
def deleted_fields(self) -> list[Field]:
def changed_files(self) -> list[File]:

def merge():
```

# Slicer

```python
def slice(
        self,
        criteria_lines: set[int],
        criteria_identifier: dict[int, set[str]],
        backward_slice_level: int,
        forward_slice_level: int,
        ignore_control: bool
        ingore_data: bool
) -> list[int]:

def backward_slice(
        criteria_lines: set[int],
        criteria_nodes: list[PDGNode],
        criteria_identifier: dict[int, set[str]],
        all_nodes: dict[int, list[PDGNode]],
        level: int,
        ignore_control: bool
        ingore_data: bool
) -> list[int]:

def forward_slice(
        criteria_lines: set[int],
        criteria_nodes: list[PDGNode],
        criteria_identifier: dict[int, set[str]],
        all_nodes: dict[int, list[PDGNode]],
        level: int,
        ignore_control: bool
        ingore_data: bool
) -> list[int]:
```
