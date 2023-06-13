The Annotated object
=====================

Type Hints
-----------

Python's type hinting syntax can be used to annotate variables, function arguments,
and return types with physical units. The following examples demonstrate the usage of type hints for annotating units:

.. code-block:: python

    # not compulsory
    meters = Annotated[float, "meters"] 
    seconds = Annotated[float, "seconds"]

    def speed(distance: "meters", time: "seconds") -> "meters / seconds":
        return distance / time


- Annotating a variable:

    .. code-block:: python

        from typing_extensions import Annotated

        distance: Annotated[float, "meters"]

- Annotating function arguments:

    .. code-block:: python

        from typing_extensions import Annotated

        def speed(distance: Annotated[float, "meters"],
                        time: Annotated[float, "seconds"]) -> 
                        Annotated[float, "meters per second"]:
            return distance / time

- Annotating function return type:

    .. code-block:: python

        from typing_extensions import Annotated

        def speed(distance: Annotated[float, "meters"],
                       time: Annotated[float, "seconds"]) -> 
                       Annotated[float, "meters per second"]:
            return distance / time

.. note::

    **Impunity** is not yet compatible with all the different syntaxes introduced
    in the `PEP 484 <https://peps.python.org/pep-0484/>`_.
