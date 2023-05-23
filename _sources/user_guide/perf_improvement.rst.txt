Static Unit Coherence Checking and AST Modification
======================================================

.. contents::

Introduction
------------

In the **Impunity** library, we emphasize the importance of statically
checking unit coherence and modifying the Abstract Syntax Tree (AST)
for improved performance. This advanced topic explains why this approach
is superior to dynamic methods, such as using if statements directly
with the Pint library.

Performance Advantages
----------------------

Statically checking unit coherence and modifying the AST offers several
performance advantages over dynamic approaches. Let's explore these
advantages in detail:

1. Early Detection of Unit Inconsistencies:

   Static analysis of annotations allows for early detection of unit
   inconsistencies during the compilation phase. This enables developers
   to catch and address unit errors before executing the code. In contrast,
   dynamic methods relying on if statements and Pint conversions only identify
   unit inconsistencies at runtime, potentially causing errors during execution.

2. Efficient and Optimized Execution:

   By modifying the AST, **Impunity** ensures that the code executes with
   coherent units, eliminating the need for runtime unit conversions. This
   results in more efficient and optimized execution, as the conversions are
   handled during the compilation process rather than repeatedly during runtime.

3. Reduced Overhead and Computational Costs:

   Statically checking the coherence of units and applying conversions at
   compile-time significantly reduces the overhead and computational costs
   associated with dynamic conversions. This can lead to improved performance,
   especially in code segments that involve complex calculations or loops.

Examples
--------

To better understand the performance advantages of static unit coherence
checking and AST modification, let's consider a couple of examples:

Example 1: Loop with Dynamic Conversion using Pint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pint

    ureg = pint.UnitRegistry()
    Q_ = ureg.Quantity

    def calculate_velocity(distance: "feet", time: "minutes") -> "ft / mn":
        converted_distance = Q_(distance, ureg.feet)
        converted_time = Q_(time, ureg.minutes)
        return converted_distance / converted_time

    distance = Q_([1, 2, 3], ureg.meter)
    time = Q_([2, 3, 4], ureg.second)

    for d, t in zip(distance, time):
        velocity = calculate_velocity(d, t)
        print(velocity)

In this example, a loop iterates over lists of `distance` and `time`
values. To perform unit conversion, each value is multiplied by the
respective Pint unit (`ureg.feet` and `ureg.minutes`). The overhead of
repeatedly performing conversions within the loop can impact performance,
especially for large datasets as it needs to check each value one by one.
It is also prone to Dimensionality Errors if `calculate_velocity` is not given
a length quantity.

Example 2: Loop with Static Coherence Checking and AST Modification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from impunity import impunity

    @impunity
    def calculate_velocity(distance: "feet", time: "minutes") -> "ft / mn":
        return distance / time

    @impunity
    def test_impunity():
        distance: "meters" = [1, 2, 3]
        time: "seconds" = [2, 3, 4]

        for d, t in zip(distance, time):
            velocity = calculate_velocity(d, t)
            print(velocity)

    test_impunity()

In this example, the `calculate_velocity` function is decorated with
`@impunity` to ensure unit coherence. The loop iterates over the lists
of `distance` and `time`, invoking the decorated function for each pair.
The static unit coherence checking and AST modification performed by 
**Impunity** eliminate the need for explicit conversions within the 
loop, resulting in improved performance.

Conclusion
----------

Static unit coherence checking and AST modification provided by the
**Impunity** library offer significant performance advantages over
dynamic approaches. By detecting unit inconsistencies early, ensuring
efficient execution, and reducing overhead and computational costs,
**Impunity** enables developers to work with coherent units
seamlessly and achieve optimal performance.

By adopting static coherence checking and AST modification,
you can enhance the performance of your code, especially
in scenarios involving complex calculations, loops, and large datasets.