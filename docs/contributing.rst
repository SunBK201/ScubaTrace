============
Contributing
============

Thank you for your interest in contributing to ScubaTrace! This document will guide you through setting up your development environment and making your first contribution.

Getting Started
===============

Development Environment Setup
-----------------------------

1. **Install Python 3.11 or later**

    Ensure you have Python 3.11 or a later version installed on your machine. You can download it from the official Python website: https://www.python.org/downloads/

2. **Clone the repository**

    Clone the ScubaTrace repository to your local machine using the following command:

    .. code-block:: bash

        git clone https://github.com/SunBK201/ScubaTrace.git

3. **Navigate to the project directory**

    Change to the project directory:

    .. code-block:: bash

        cd ScubaTrace

4. **Install the required packages**

    Install the necessary packages using pip:

    .. code-block:: bash

        pip install -r requirements.txt

Making Changes
==============

1. **Create a new branch**

    Create a new branch for your changes:

    .. code-block:: bash

        git checkout -b your-branch-name

2. **Make your changes**

    Make the necessary changes to the codebase.

3. **Run tests**

    Ensure that all tests pass before committing your changes. You can run the tests using:

    .. code-block:: bash

        pytest

4. **Commit your changes**

    Commit your changes with a meaningful commit message:

    .. code-block:: bash

        git commit -m "Description of your changes"

5. **Push your changes**

    Push your changes to your forked repository:

    .. code-block:: bash

        git push origin your-branch-name

6. **Create a pull request**

    Open a pull request on the main repository. Provide a clear description of your changes and any relevant information.

Code Style
==========

Please follow the PEP 8 style guide for Python code. You can use tools like `flake8` to check your code for style issues:

.. code-block:: bash

    pip install flake8
    flake8 .

Thank you for contributing!
