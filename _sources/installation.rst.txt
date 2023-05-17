Installation
============

The impunity library checks statically for any unit annotation in the code 
and eventually modify it to add conversions if necessary. To do so, it uses
the `Pint <https://pint.readthedocs.io/en/stable/>`_ to check if units in
annotations are compatible.

The best way to install impunity is to use pip in a Python >= 3.8 environment:

 .. code:: bash

    # installation
    pip install impunity

Contribute to impunity
------------------------------------------------

If you intend to contribute to impunity or file a pull request, the best way to
ensure continuous integration does not break is to reproduce an environment with
the same exact versions of all dependency libraries.

The following steps **are not mandatory**, but they will ensure a swift
reviewing process:

- install `poetry <https://python-poetry.org/>`_ on your workstation
- install impunity with poetry:

  .. code:: bash

      git clone --depth 1 https://github.com/achevrot/impunity
      cd impunity/
      poetry install -E all

  Then, you may:

  - prefix all your commands with ``poetry run``
  - or run a shell with all environment variables properly set with ``poetry
    shell``
