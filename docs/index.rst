==========
ScubaTrace
==========

ScubaTrace is a code analysis toolkit that leverages tree-sitter and LSP (Language Server Protocol) to provide parsing, analysis, and context extraction capabilities for multiple programming languages.

Unlike most traditional static analysis tools that rely on compilation to extract Intermediate Representation (IR) for code analysis, ScubaTrace delivers analysis capabilities even when code repositories are incomplete or unable to compile. This resilience makes it particularly valuable for scenarios where traditional analysis approaches would fail, enabling developers and security researchers to gain insights from code that might otherwise be inaccessible to conventional static analysis methodologies.

ScubaTrace serves as a portable analysis solution for IDE development, AI-powered coding tools, and SAST (Static Application Security Testing).


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

Features
===================

- **Multi-Language Support**
- **No Need To Compile**
- **Statement-Based AST Abstraction**
- **Code Call Graph**
- **Code Control Flow Graph**
- **Code Data/Control Dependency Graph**
- **References Inference**
- **CPG Based Multi-Granularity Slicing**
- **Built on Tree-sitter and LSP**

Supported Languages
===================

ScubaTrace supports multiple programming languages, including:

===================  ===========================  ========================
Language             Language Server              Tree-sitter Parser
===================  ===========================  ========================
C/C++                clangd                       tree-sitter-cpp
Java                 Eclipse JDT LS               tree-sitter-java
Python               jedi-language-server         tree-sitter-python
JavaScript           typescript-language-server   tree-sitter-javascript
Go                   gopls                        tree-sitter-go
Rust                 Rust Analyzer                tree-sitter-rust
Ruby                 Solargraph                   tree-sitter-ruby
Swift                SourceKit-LSP                tree-sitter-swift
C#                   OmniSharp                    tree-sitter-c-sharp
PHP                  phpactor                     tree-sitter-php
===================  ===========================  ========================

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
