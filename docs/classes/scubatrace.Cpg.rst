Cpg
=====

ScubaTrace can read Joern ``cpg.bin`` files and expose them as an in-memory
code property graph. The graph keeps Joern node labels and properties while
adding Python helpers for common navigation tasks, such as finding methods,
walking edges, resolving call targets, and locating the method that contains a
source position.

Loading a Cpg
-------------

Use :class:`scubatrace.Cpg` when you already have a Joern FlatGraph file:

.. code-block:: python

    import scubatrace

    cpg = scubatrace.Cpg.load("path/to/cpg.bin")

    print(cpg.node_count)
    print(cpg.edge_count)

When a project is created with :class:`scubatrace.JoernConfig`, ScubaTrace also
stores the loaded graph on the project:

.. code-block:: python

    import scubatrace

    project = scubatrace.Project.create(
        "path/to/code",
        language=scubatrace.language.C,
        joern_config=scubatrace.JoernConfig(),
    )

    cpg = project.cpg

Querying Nodes
--------------

Nodes are keyed by ``(label, sequence)`` tuples. For ad-hoc exploration, use
label-based helpers or Joern-style step names:

.. code-block:: python

    methods = cpg.nodes_by_label("METHOD")
    calls = cpg.nodes_by_label("CALL")

    # Dynamic CPG node steps are also available.
    methods = cpg.method
    calls = cpg.call

    main = cpg.find_method("main")
    matching = cpg.find_methods(".*Controller.*", regex=True)

CPG properties can be read from the raw ``properties`` mapping, with
:meth:`scubatrace.CpgNode.get`, or through lower-case Python attributes for
properties defined by the CPG schema:

.. code-block:: python

    method = cpg.find_method("main")
    if method is not None:
        print(method["NAME"])
        print(method.get("FULL_NAME"))
        print(method.full_name)

Navigating Edges
----------------

Use edge helpers when you need graph-level traversal:

.. code-block:: python

    method = cpg.find_method("main")
    if method is not None:
        contained_nodes = list(cpg.successors(method.id, "CONTAINS"))
        incoming_calls = list(cpg.predecessors(method.id, "CALL"))
        outgoing_edges = list(cpg.out_edges(method.id))

Call Relationships
------------------

For ``METHOD`` nodes, :attr:`scubatrace.CpgNode.callers` and
:attr:`scubatrace.CpgNode.callees` return :class:`scubatrace.cpg.MethodCall`
objects. Each relationship contains the caller method, callee method, and the
callsite node. Unresolved calls keep ``callee`` as ``None``.

.. code-block:: python

    method = cpg.find_method("main")
    if method is not None:
        for relation in method.callees:
            callee_name = relation.callee.full_name if relation.callee else "<unresolved>"
            location = relation.callsite_location
            print(callee_name, location.filename, location.line_number)

Source Locations
----------------

Use :meth:`scubatrace.Cpg.methods_at` or :meth:`scubatrace.Cpg.method_at` to map
a source location back to the smallest matching CPG method:

.. code-block:: python

    method = cpg.method_at("src/main.c", 42)
    exact = cpg.method_at("src/main.c", 42, column_number=8)

The returned nodes expose :attr:`scubatrace.CpgNode.location`, which normalizes
file, line, column, and byte-offset fields into a
:class:`scubatrace.SourceLocation` object.

NetworkX Export
---------------

Use :meth:`scubatrace.Cpg.to_networkx` to convert the Cpg into a
``networkx.MultiDiGraph``. Node attributes include the Cpg label and all node
properties. Edge attributes include the edge label and optional edge property.

.. code-block:: python

    graph = cpg.to_networkx()

.. autoclass:: scubatrace.Cpg
   :members:
   :show-inheritance:

.. autoclass:: scubatrace.CpgNode
   :members:
   :show-inheritance:

.. autoclass:: scubatrace.CpgEdge
   :members:
   :show-inheritance:

.. autoclass:: scubatrace.cpg.MethodCall
   :members:
   :show-inheritance:

.. autoclass:: scubatrace.SourceLocation
   :members:
   :show-inheritance:

.. autoclass:: scubatrace.cpg.FlatGraphReader
   :members:
   :show-inheritance:

.. autofunction:: scubatrace.cpg.load
