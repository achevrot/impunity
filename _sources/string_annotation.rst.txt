String Annotations
============================


**Impunity** supports various annotation styles for denoting physical units in code.
It uses the `Pint <https://pint.readthedocs.io/en/stable/>`_ library under the hood
to check unit consistency and find conversion values.

Thanks to Pint string parsing, units can be defined as strings of different types
in annotations:

.. code-block:: python

    @impunity
    def speed(distance: "meters", time: "s") -> "meters / seconds":
        return distance / time

A string in an annotation checked by impunity not corresponding to any kind
of unit will result in a warning:

.. code-block:: python

    @impunity
    def speed(distance: "stadium", time: "s") -> "meters / seconds":
        return distance / time

    # Warning : 'stadium' is not a unit recognized by Pint

Note however that as is, type checkers like mypy will return an error
as `meters` or `s` are undefined. Please visit :doc:`annotated` to use impunity
alongside mypy or another type checker.