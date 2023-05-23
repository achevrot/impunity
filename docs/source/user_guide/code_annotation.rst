Supported Annotation Styles
============================


**Impunity** supports various annotation styles for denoting physical units in code. This section provides an overview of the supported styles along with syntax examples and guidelines for their usage.

Type Hints
-----------

Python's type hinting syntax can be used to annotate variables, function arguments, and return types with physical units. The following examples demonstrate the usage of type hints for annotating units:

- Annotating a variable:

    .. code-block:: python

        from typing_extensions import Annotated

        distance: Annotated[float, "meters"]

- Annotating function arguments:

    .. code-block:: python

        from typing_extensions import Annotated

        def calculate_speed(distance: Annotated[float, "meters"], time: Annotated[float, "seconds"]) -> Annotated[float, "meters per second"]:
            return distance / time

- Annotating function return type:

    .. code-block:: python

        from typing_extensions import Annotated

        def calculate_velocity(distance: Annotated[float, "meters"], time: Annotated[float, "seconds"]) -> Annotated[float, "meters per second"]:
            return distance / time


String Annotations
------------------

**Impunity** also supports string annotations as an alternative approach. 
By assigning the unit to a variable and using it in annotations, you can directly 
annotate variables, function arguments, and return types using type hints with string annotations. Here's an example:

.. code-block:: python

    from typing_extensions import Annotated

    meters = Annotated[float, "meters"]
    seconds = Annotated[float, "seconds"]

    def calculate_speed(distance: "meters", time: "seconds") -> Annotated[float, "meters per second"]:
        return distance / time

* In this example, the `meters` and `seconds` variables hold the annotated types, and they can be used to annotate other variables, function arguments, and return types directly.

* Please note that the definition of the `meters` and `seconds` variables are not compulsory. They only make sure static typing library like mypy do not raise errors.
