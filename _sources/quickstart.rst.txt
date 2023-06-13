Getting started
===============

**Impunity** (/ɪmˈpjuː.nə.ti/) is a Python library that enables static analysis of code 
annotations to ensure coherence and consistency of physical units. It 
provides a framework for developers to annotate their Python code with 
physical units and automatically verifies if the units are compatible and 
adhere to predefined coherence rules.


This guide will help you get started with using **Impunity** to ensure
coherence and consistency of physical units in your Python code. To do so, it uses
the `Pint <https://pint.readthedocs.io/en/stable/>`_ library to check if units in
annotations are compatible between each other. 

Installation
------------

The best way to install impunity is to use pip in a Python >= 3.8 environment:

 .. code-block:: bash

    pip install impunity


Usage
-----

Using **Impunity** is straightforward. Follow the steps below to integrate it into your code:

   .. code-block:: python

        # 1: Import the necessary decorator from the Impunity library:

        from impunity import impunity

        # 2: Annotate your code with appropriate units:

        distance: "meters" = 10
        time: "seconds" = 10
        
        # 3: Apply the @impunity decorator to functions or methods that you want to check

        @impunity
        def speed(distance: "meters", time: "seconds") -> "meters / seconds":
            return distance / time

        speed(distance, time) # return 1

**Impunity** checks the units in annotations statically, **before** execution.
When inconsistencies are found in the decorated code, conversion
are performed under the hood when possible:

   .. code-block:: python

       @impunity
        def speed(distance: "meters", time: "seconds") -> "km / h":
            return distance / time
        
        speed(distance, time) # return 3.6

When inconsistencies cannot be fixed through conversion, warnings are raised
with hints on how to correct the code:

   .. code-block:: python

       @impunity
       def speed(distance: "meters", time: "seconds") -> "kelvin":
           return distance / time

        Warning: "Incompatible unit returned"


.. - The most simple usage consists of using units placed as annotations. The code is checked and rewritten if need be when decorated.


.. - You can define unit shortcuts with the Annotations from typing to avoid mypy errors:

.. .. code:: python

..     if sys.version_info >= (3, 9):
..         from typing import Annotated
..     else:
..         from typing_extensions import Annotated

..     m = Annotated[Any, "m"]
..     s = Annotated[Any, "s"]

.. - Then you can use the decorator ``@impunity`` to check the functions:

.. .. code:: python

..     from impunity import impunity

..     @impunity
..     def speed(distance: "m", time: "s") -> "m/s":
..         return distance / time

..     @impunity
..     def regular_conversion():
..         altitudes: "ft" = np.arange(0, 1000, 100)
..         duration: "mn" = 100
..         result = speed(altitudes, duration)
..         print(result)  # results in m/s

..         result_imperial: "ft/mn" = speed(altitudes, duration)
..         print(result_imperial)  # results in ft/mn

..     if __name__ == "__main__":
..         regular_conversion()

.. In the example above, the function ``regular_conversion()`` is rewritten as follows to yield the correct results:

.. .. code:: python

..     @impunity
..     def regular_conversion():
..         altitudes: "ft" = np.arange(0, 1000, 100)
..         duration: "mn" = 100
..         result = speed(altitudes * 0.3048, duration * 60) # convert to expected units
..         print(result)

..         result_imperial: "ft/mn" = speed(altitudes, duration) * 196.85039 # convert to expected units
..         print(result_imperial)

.. - The check fails if units are inconsistent:

..  .. code:: python

..     @impunity
..     def inconsistent_units():
..         temperatures: "K" = np.arange(0, 100, 10)
..         duration: "s" = 6000
..         return speed(temperatures, duration)

.. The call to ``speed()`` here will raise a warning and be ignored by impunity because the temperatures
.. in Kelvin cannot be converted in meters.
