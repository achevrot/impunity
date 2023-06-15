.. Impunity documentation master file, created by
   sphinx-quickstart on Tue May 16 11:02:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:sd_hide_title:

Impunity
====================================





.. div:: sd-bg-primary
   

   .. grid::
      :reverse:
      :gutter: 2 3 3 3
      :margin: 4 4 1 2

      .. grid-item::
         :columns: 12 4 4 4
         :child-align: justify
         :class: sd-text-white sd-fs-3


      .. grid-item::
         :columns: 12 8 8 8
         :child-align: justify
         :class: sd-text-white sd-fs-3

         A Python library to check your physical units effortlessly.


         .. button-ref:: quickstart
            :ref-type: doc
            :outline:
            :color: white
            :class: sd-px-4 sd-fs-5


Easy to use
   Based on a decorator, to add on any annotated function or class

Support for various annotation styles
   Usable with Annotated object or string annotations

Integration with popular Python type checkers.
   Can be used along mypy for powerful typing systems

No additional runtime overhead
   Impunity works directly on the AST for a static analysis of your code

.. grid:: 2
   
    .. grid-item::

      .. code-block:: python

               @impunity
               def speed(d: "m", t: "s") -> "m / s":
                  return d / t

               speed(10, 10) # returns 1

    .. grid-item::

      .. code-block:: python

               @impunity
               def speed(d: "m", t: "s") -> "km / h":
                  return d / t

               speed(10, 10) # returns 3.6

    .. grid-item::

      .. code-block:: python

               @impunity
               def speed(d: "m", t: "s") -> "feet":
                  return d / t

               # Warning: "Incompatible unit returned"

    .. grid-item::

      .. code-block:: python

               @impunity
               def speed(d: "m", t: "s") -> "m / s":
                  return d + t

               Warning: "Types are not compatible"

.. toctree::
   
   quickstart


.. toctree::
   :caption: API
   :hidden:

   api

.. toctree::
   :caption: Annotations
   :hidden:

   string_annotation
   annotated

.. toctree::
   :caption: Advanced Topic
   :hidden:

   how
   perf_improvement

.. toctree::
   :hidden:

   contribute

.. note::

   This project is under active development.