Contribute to impunity
============

Source code on `github <https://github.com/achevrot/impunity>`_

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

