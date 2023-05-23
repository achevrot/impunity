Getting started
===============

This guide will help you get started with using **Impunity** to ensure
coherence and consistency of physical units in your Python code. To do so, it uses
the `Pint <https://pint.readthedocs.io/en/stable/>`_ to check if units in
annotations are compatible. 

Installation
------------

The best way to install impunity is to use pip in a Python >= 3.8 environment:

 .. code-block:: bash

    # installation
    pip install impunity


Usage
-----

Using **Impunity** is straightforward. Follow the steps below to integrate it into your code:

1. Import the necessary decorator from the **Impunity** library:

   .. code-block:: python

       from impunity import impunity

2. Annotate your code with appropriate units:

   Use annotations to specify the units for variables, function parameters, and return types. For example:

   .. code-block:: python

       distance: "meters"
       time: "seconds"

3. Use the **Impunity** decorator:

   Apply the `@impunity` decorator to functions or methods that you want to check for unit coherence. For example:

   .. code-block:: python

       @impunity
       def calculate_speed(distance: "meters", time: "seconds") -> "meters / seconds":
           return distance / time

   The **Impunity** decorator will analyze the annotations and automatically correct the code if any unit inconsistencies are found.

5. Review the feedback:

   When running **Impunity**, it will analyze your code and provide feedback
   on any detected unit inconsistencies. The feedback will include information
   on the source of the inconsistency and any applied conversions.

   .. note::

      **Impunity** performs static analysis, provides feedback and modify the code executed directly.
      Manual review may be necessary to ensure correctness.

Examples
--------

Here are a few examples to illustrate how to use **Impunity**:

1. Basic Unit Checking:

   .. code-block:: python

       from impunity import impunity

       @impunity
       def calculate_speed(distance: "meters", time: "seconds") -> "meters / seconds":
           return distance / time

   In this example, the `calculate_speed` function is decorated with
   `@impunity`. **Impunity** will analyze the annotations of the
   `distance` and `time` parameters and ensure unit coherence. In this case,
   nothing is changed as the units are coherent.

2. Unit Conversion:

   .. code-block:: python

       from impunity import impunity

       @impunity
       def calculate_speed(distance: "meters", time: "seconds") -> "kilometers / hour":
           return distance / time

   In this example, the `calculate_speed` function is also decorated with
   `@impunity`. **Impunity** will find the inconsistency between the parameters
   of the function and its return value. It will automatically apply a conversion
   value to both `distance` and `time` in order to return the correct units.

Conclusion
----------

Congratulations! You have successfully installed and started using **Impunity** to 
ensure unit coherence and consistency in your Python code. By leveraging annotations 
and automatic unit conversion, **Impunity** helps catch unit inconsistencies early 
in the development process, leading to more accurate and reliable code.

Next, you can explore the :doc:`user_guide`




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
