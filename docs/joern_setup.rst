===========
Joern Setup
===========

ScubaTrace can use `Joern <https://joern.io/>`_ as an optional backend for
code property graph (CPG) analysis. When Joern is enabled, ScubaTrace either
runs ``joern-parse`` for the project source directory or loads an existing
``cpg.bin`` file, then exposes the result as :class:`scubatrace.Cpg` on
``project.cpg``.

Install Joern
=============

Joern is distributed as ``joern-cli``. Follow the official installation guide
for the latest platform-specific details:
`Joern Installation <https://docs.joern.io/installation/>`_.

The official pre-built binary installer requires a JDK. Joern's documentation
currently recommends JDK 19:

.. code-block:: bash

    mkdir joern
    cd joern
    curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" -o joern-install.sh
    chmod u+x joern-install.sh
    ./joern-install.sh --interactive

By default, the installer places Joern under ``~/bin/joern``. ScubaTrace needs
the ``joern-parse`` executable. You can either add Joern's CLI directory to
``PATH``:

.. code-block:: bash

    export PATH="$HOME/bin/joern/joern-cli:$PATH"
    joern-parse --help

or provide the executable path directly in :class:`scubatrace.JoernConfig`:

.. code-block:: python

    joern_config = scubatrace.JoernConfig(
        joern_parse_path="/Users/you/bin/joern/joern-cli/joern-parse",
    )

For large codebases, Joern may need additional JVM heap memory. Configure that
in your Joern installation or point ``joern_parse_path`` to a wrapper script
that invokes ``joern-parse`` with the required JVM settings.

Enable Joern in ScubaTrace
==========================

Pass :class:`scubatrace.JoernConfig` to :meth:`scubatrace.Project.create`:

.. code-block:: python

    import scubatrace

    joern_config = scubatrace.JoernConfig(
        enable=True,
        Language=scubatrace.language.C,
    )

    project_with_joern = scubatrace.Project.create(
        "path/to/your/codebase",
        language=scubatrace.language.C,
        joern_config=joern_config,
    )

    cpg = project_with_joern.cpg

ScubaTrace runs ``joern-parse`` during project initialization, stores the
generated ``cpg.bin`` path on ``project.cpg_path``, and loads the graph into
``project.cpg``.

Configure CPG Output
====================

Use ``cpg_output_dir`` to control where Joern writes ``cpg.bin``. If the output
directory already exists, set ``overwrite=True`` only when it is safe to replace
that directory:

.. code-block:: python

    joern_config = scubatrace.JoernConfig(
        cpg_output_dir="build/joern-cpg",
        overwrite=True,
        Language=scubatrace.language.C,
    )

If ``cpg_output_dir`` is omitted, ScubaTrace creates a temporary directory for
the Joern output.

Reuse an Existing CPG
=====================

If ``cpg_path`` points to an existing ``cpg.bin`` file, ScubaTrace skips
``joern-parse`` and loads that file directly:

.. code-block:: python

    joern_config = scubatrace.JoernConfig(
        cpg_path="path/to/cpg.bin",
    )

    project_with_joern = scubatrace.Project.create(
        "path/to/your/codebase",
        language=scubatrace.language.C,
        joern_config=joern_config,
    )

Language Selection
==================

Set ``Language`` to pass Joern's explicit ``--language`` argument. This avoids
relying on Joern's language auto-detection.

=======================  ===================
ScubaTrace language      Joern language
=======================  ===================
``language.C``           ``newcpp``
``language.JAVA``        ``javasrc``
``language.PYTHON``      ``python``
``language.JAVASCRIPT``  ``javascript``
=======================  ===================

Unsupported languages raise :class:`ValueError` when explicit Joern language
selection is requested.

Direct Parsing
==============

You can also call the lower-level parser directly and load the generated CPG:

.. code-block:: python

    import scubatrace
    from scubatrace import joern

    cpg_path = joern.parse(
        "path/to/your/codebase",
        joern.JoernConfig(Language=scubatrace.language.C),
    )

    cpg = scubatrace.Cpg.load(str(cpg_path))

Troubleshooting
===============

``joern-parse`` must be installed and available on ``PATH`` unless
``joern_parse_path`` points to the executable. ScubaTrace raises
:class:`FileNotFoundError` when it cannot find the executable.

If ``cpg_output_dir`` already exists and ``overwrite`` is ``False``, ScubaTrace
raises :class:`FileExistsError`.

Set ``enable=False`` only when a configuration object must be passed around but
Joern should not run. Calling ``joern.parse`` with disabled integration raises
:class:`ValueError`.

Joern API Reference
===================

.. autoclass:: scubatrace.JoernConfig
   :members:
   :show-inheritance:

.. autofunction:: scubatrace.joern.parse
