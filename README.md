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
