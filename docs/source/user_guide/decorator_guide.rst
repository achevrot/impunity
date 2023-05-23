Impunity Decorator Guide
================================

.. contents::

Introduction
------------

The **Impunity** library provides a powerful decorator that performs 
static analysis of annotations in your Python code, ensuring coherence 
and consistency of physical units. By applying the `@impunity` decorator 
to your functions or methods, **Impunity** automatically detects unit 
inconsistencies and rewrites the code with proper conversion values 
taken from the Pint library.

Usage
-----

Using the **Impunity** decorator is straightforward. Follow the steps 
below to apply the decorator to your functions or methods:

1. Import the `impunity` decorator from the **Impunity** library:

   .. code-block:: python

       from impunity import impunity

2. Apply the `@impunity` decorator to the functions or methods you 
want to check for unit coherence:

   .. code-block:: python

       @impunity
       def calculate_speed(distance: "meters", time: "seconds") -> "m/s":
           return distance / time

   The **Impunity** decorator will analyze the annotations of the 
   function parameters and return type, automatically detecting 
   any unit inconsistencies.

3. Run your code:

   Execute your code as usual. If any unit inconsistencies are 
   detected by **Impunity**, it will rewrite the code with proper 
   conversion values and execute the modified version.

4. Review the modified code:

   After executing the decorated function or method, **Impunity** 
   will modify the code to include the necessary conversions for 
   unit coherence. The modified code will be executed, ensuring coherent results.

Examples
--------

Here are a few examples to illustrate how the **Impunity** decorator works:

Example 1: Converting between meters and kilometers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from impunity import impunity

    @impunity
    def calculate_distance_in_km(distance: "meters") -> "kilometers":
        return distance

In this example, the `calculate_distance_in_km` function
is decorated with `@impunity`. If the `distance` parameter
is annotated with the unit "meters", **Impunity** will automatically
rewrite the code to include the conversion from meters to kilometers.

Example 2: Coherence checking with multiple parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from impunity import impunity

    @impunity
    def calculate_velocity(distance: "meters", time: "seconds") -> "m/s":
        return distance / time

In this example, the `calculate_velocity` function is decorated with 
`@impunity`. **Impunity** analyzes the annotations of both the `distance` 
and `time` parameters and ensures that their units are coherent. If any 
unit inconsistencies are detected, the decorator rewrites the code with 
the proper conversion values to ensure that meters per second are returned.

Example 3: Coherence checking with custom units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from **Impunity** import impunity

    meters = "meters"
    kilometers = "kilometers"

    @impunity
    def calculate_distance_in_km(distance: float) -> float:
        return distance / 1000

In this example, custom units are defined as strings (`meters` 
and `kilometers`). The `calculate_distance_in_km` function is decorated 
with `@impunity`, and **Impunity** ensures coherence between the annotated 
unit of `distance` and the expected unit.

Conclusion
----------

The **Impunity** decorator is a powerful tool for maintaining unit coherence 
and consistency in your Python codebase. By automatically analyzing annotations 
and rewriting the code with proper conversion values, it helps catch unit 
inconsistencies and ensures accurate results. Incorporate the **Impunity** 
decorator into your code to work confidently with physical quantities.

Make sure to thoroughly test your code and review the modified code produced 
by the decorator. **Impunity** uses the Pint library to perform unit 
conversions, providing accurate and reliable results. With **Impunity**, 
you can focus on developing your application while ensuring unit coherence 
in a hassle-free manner.

Next, you may want to explore the :doc:`decorator_options` 
provided by the `@impunity` decorator further enhance your unit 
coherence checking capabilities.