===============
Getting Started
===============

This guide will help you get started with ScubaTrace, a tool for analyzing and tracing C projects.

Installation
============

To install ScubaTrace, use pip:

.. code-block:: bash

    pip install scubatrace

Usage
=====

Here is a basic example of how to use ScubaTrace to analyze a C project:

.. code-block:: python

    import scubatrace
    
    # Initialize the project
    a_proj = scubatrace.CProject("../tests")
    
    # Access and print various elements of the project
    print(a_proj.files["src/test.c"].structs[0].name)
    print(a_proj.files["src/test.c"].functions["foo"].name)
    print(a_proj.files["src/test.c"].functions["foo"].calls)
    print(a_proj.files["src/test.c"].functions["foo"].callee)
    print(a_proj.files["src/test.c"].functions["foo"].caller)
    print(a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].ref_statements)
    print(a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].definition)
    print(a_proj.dependencies)
    print(a_proj.licenses)

Explanation
===========

- **a_proj.files["src/test.c"].structs[0].name**: Prints the name of the first struct in `src/test.c`.
- **a_proj.files["src/test.c"].functions["foo"].name**: Prints the name of the function `foo` in `src/test.c`.
- **a_proj.files["src/test.c"].functions["foo"].calls**: Prints the calls made by the function `foo`.
- **a_proj.files["src/test.c"].functions["foo"].callee**: Prints the functions called by `foo`.
- **a_proj.files["src/test.c"].functions["foo"].caller**: Prints the functions that call `foo`.
- **a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].ref_statements**: Prints the reference statements of the first variable in the first statement of `foo`.
- **a_proj.files["src/test.c"].functions["foo"].statements[0].variables[0].definition**: Prints the definition of the first variable in the first statement of `foo`.
- **a_proj.dependencies**: Prints the dependencies of the project.
- **a_proj.licenses**: Prints the licenses of the project.

For more detailed information, refer to the official documentation.