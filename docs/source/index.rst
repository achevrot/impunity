.. Impunity documentation master file, created by
   sphinx-quickstart on Tue May 16 11:02:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Impunity's documentation!
====================================

Source code on `github <https://github.com/achevrot/impunity>`_

**Impunity** (/ɪmˈpjuː.nə.ti/) is a Python library that enables static analysis of code 
annotations to ensure coherence and consistency of physical units. It 
provides a framework for developers to annotate their Python code with 
physical units and automatically verifies if the units are compatible and 
adhere to predefined coherence rules.

Features
====================================

* Automatic verification of physical unit coherence in annotated Python code.
* Support for various annotation styles, including type hints, or custom annotations.
* Flexible and extensible rule-based system using the Pint library.
* Integration with popular Python development environments and build systems as mypy.
* Fast and efficient parsing and analysis of annotations using Python's abstract syntax tree (AST).
* Detailed error reporting with actionable suggestions for resolving unit coherence issues.
* Easy integration into existing workflows and projects.


Contents
========

.. toctree::
   :maxdepth: 1

   quickstart
   user_guide
   contribute

.. note::

   This project is under active development.