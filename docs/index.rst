==========
ScubaTrace
==========

Next-generation codebase analysis toolkit.

.. image:: _static/ScubaTrace.png
    :width: 500px
    :alt: ScubaTrace

.. caution::

    This project is still in development and not ready for production use.

Install
==========

1. Install ScubaTrace:

.. code-block:: bash

    pip install scubatrace

2. Import it to your project:

.. code-block:: python

    import scubatrace

.. toctree::
    :caption: Usage
    :hidden:

    usage

Supported Languages
===================

ScubaTrace supports multiple programming languages, including:

==========   ========
Language     Maturity
==========   ========
C/C++        High
Java         High
Python       High
JavaScript   High
Go           Medium
Rust         Medium
Ruby         Medium
Swift        Medium
C#           Medium
PHP          Medium
==========   ========

Reference
==========
.. autosummary::
   :toctree: classes
   :caption: Reference
   :nosignatures:

   scubatrace.Project
   scubatrace.File
   scubatrace.Function
   scubatrace.Statement
   scubatrace.Identifier
   scubatrace.Parser
   scubatrace.Language

.. toctree::
    :caption: DEVELOPMENT
    :hidden:

    contributing
    GitHub <https://github.com/SunBK201/ScubaTrace>
    license

Source Code
===========

GitHub: `https://github.com/SunBK201/ScubaTrace <https://github.com/SunBK201/ScubaTrace>`_
