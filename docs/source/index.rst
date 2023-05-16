.. Impunity documentation master file, created by
   sphinx-quickstart on Tue May 16 11:02:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Impunity's documentation!
====================================

Source code on `github <https://github.com/achevrot/impunity>`_

**Impunity** (/ɪmˈpjuː.nə.ti/) is a Python library for the users of physical
quantities.

Its main purpose is to check the consistency of physical units with minimal
overhead. It uses *flexible variable and function annotations* 
(`PEP 593 <https://peps.python.org/pep-0593/>`_) to check *before* runtime the 
consistency between variables and arguments of functions. If physical units 
are consistent, impunity rewrites the code by automatically applying 
conversions in the code of the function.

Contents
========

.. toctree::
   :maxdepth: 1

   installation
   quickstart
   user_guide
   gallery
   api_reference
   publications

.. note::

   This project is under active development.