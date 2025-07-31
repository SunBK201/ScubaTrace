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

    # Initialize a ScubaTrace Project
    # language can be set to one of the following:
    # scubatrace.language.[C, JAVA, PYTHON, JAVASCRIPT, GO, RUST, RUBY, PHP, CSHARP, SWIFT]
    project = scubatrace.Project.create("path/to/your/codebase", language=scubatrace.language.C)

.. note::

    Incomplete or broken codebases may cause parsing errors that could result in inaccurate analysis results.

.. code-block:: python

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
    criteria_lines = [10, 12, 18]
    sliced_statements = function.slice_by_lines(
        lines=criteria_lines, control_depth=5, data_dependent_depth=8
    )

    # Get tree-sitter node in a file/function/statement
    file_node = file.node
    function_node = function.node
    statement_node = statement.node


For more detailed information, refer to the Reference.
