===============
Getting Started
===============

This guide will help you get started with ScubaTrace.

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
    project = scubatrace.Project.Project(".", scubatrace.language.C)
    
    # Access and show various elements of the project
    print(project.files["src/test.c"].functions["foo"].name)
    print(project.files["src/test.c"].functions["foo"].calls)
    print(project.files["src/test.c"].functions["foo"].callee)
    print(project.files["src/test.c"].functions["foo"].caller)
    print(project.files["src/test.c"].functions["foo"].statements[0].variables[0].references)
    print(project.files["src/test.c"].functions["foo"].statements[0].variables[0].definitions)

Explanation
===========

- **project.files["src/test.c"].functions["foo"].name**: Prints the name of the function `foo` in `src/test.c`.
- **project.files["src/test.c"].functions["foo"].calls**: Prints the calls made by the function `foo`.
- **project.files["src/test.c"].functions["foo"].callee**: Prints the functions called by `foo`.
- **project.files["src/test.c"].functions["foo"].caller**: Prints the functions that call `foo`.
- **project.files["src/test.c"].functions["foo"].statements[0].variables[0].references**: Prints the reference statements of the first variable in the first statement of `foo`.
- **project.files["src/test.c"].functions["foo"].statements[0].variables[0].definitions**: Prints the definition of the first variable in the first statement of `foo`.

For more detailed information, refer to the official documentation.
