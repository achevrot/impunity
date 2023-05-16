Getting started
===============

- The most simple usage consists of using units placed as annotations. The code is checked and rewritten if need be when decorated.


- You can define unit shortcuts with the Annotations from typing to avoid mypy errors:

.. code:: python

    if sys.version_info >= (3, 9):
        from typing import Annotated
    else:
        from typing_extensions import Annotated

    m = Annotated[Any, "m"]
    s = Annotated[Any, "s"]

- Then you can use the decorator ``@impunity`` to check the functions:

.. code:: python

    from impunity import impunity

    @impunity
    def speed(distance: "m", time: "s") -> "m/s":
        return distance / time

    @impunity
    def regular_conversion():
        altitudes: "ft" = np.arange(0, 1000, 100)
        duration: "mn" = 100
        result = speed(altitudes, duration)
        print(result)  # results in m/s

        result_imperial: "ft/mn" = speed(altitudes, duration)
        print(result_imperial)  # results in ft/mn

    if __name__ == "__main__":
        regular_conversion()

In the example above, the function ``regular_conversion()`` is rewritten as follows to yield the correct results:

.. code:: python

    @impunity
    def regular_conversion():
        altitudes: "ft" = np.arange(0, 1000, 100)
        duration: "mn" = 100
        result = speed(altitudes * 0.3048, duration * 60) # convert to expected units
        print(result)

        result_imperial: "ft/mn" = speed(altitudes, duration) * 196.85039 # convert to expected units
        print(result_imperial)

- The check fails if units are inconsistent:

 .. code:: python

    @impunity
    def inconsistent_units():
        temperatures: "K" = np.arange(0, 100, 10)
        duration: "s" = 6000
        return speed(temperatures, duration)

The call to ``speed()`` here will raise a warning and be ignored by impunity because the temperatures
in Kelvin cannot be converted in meters.
