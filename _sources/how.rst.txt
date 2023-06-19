How Does It Work ?
==================

Reminder on Decorators 
**********************

In Python, a decorator function in Python is a higher order function which changes the behaviour
of a given function. Let’s consider an illustrative code snippet to understand how impunity operates
in practice. Suppose we have the following Python function:

.. code-block:: python

    def speed(distance: "meters", duration: "seconds") -> "km/h":
        res = distance / duration
        return res

If we use the following decorator function, at definition time, the following code is executed and the
same function is returned:

.. code-block:: python

    def decorator(function):
        print(f"Function definition for {function.__name__}")
        return function

    @decorator
    def speed(distance: "meters", duration: "seconds") -> "km/h":
        ...
    
    >>> speed = decorator(speed)
    Function definition for speed

In practice, decorator functions are mostly used to change the behaviour of functions at runtime. A
common example is the logging of the execution of a function, or the timing of its execution. Then
a new (nested) function must be defined based on the old one:

.. code-block:: python

    def logger(function):
        def new_function(*args):
            print(f"Executing function {function.__name__} with parameters {args}")
            return function(*args)
        return new_function

        @logger
        def speed(distance: "meters", duration: "seconds") -> "km/h":
            res = distance / duration
            return res

        >>> speed(1, 2)
        Executing function speed with parameters (1, 2)
        0.5

The impunity library provides the @impunity decorator in order to check the coherence of physical
units defined within the code: it traverses (and sometimes modifies) the Abstract Syntax Tree (AST)
of the code for the function. Annotated variables and functions are logged for future reference. The
AST of our speed function can be depicted in a visual representation, as shown below:

.. figure:: images/ast_origin.svg
   :name: base_ast

As the decorator function walks through the AST, variables annotated with units of measures (i.e.
distance and duration) are logged. Then, each time a call to an annotated function is detected,
@impunity compares the expected units of measures from function parameters and return values with
the units specified in the function definition. When a mismatch is detected, indicating an
inconsistency in units, impunity takes one of the following actions:


- if the two units are commensurable, @impunity modifies the AST to include a conversion operation;
- if the two units are not commensurable, an IncommensurableUnits warning is raised.

.. figure:: images/test.svg
   :name: diagram



In the case of the speed function example, the expected return UoM is "km/h" while the UoM inferred
from the division between distance and duration variables is "m/s". impunity identifies this discrepancy
and takes action by modifying the AST accordingly. It introduces a binary operation (BinOp)
node to convert the result to the proper UoM, as depicted in red on this modified AST:

.. figure:: images/ast_modif.svg
   :name: modif_ast

Here, the constant value of 3.6 is calculated by determining the conversion factor between the two
units "m/s" and "km/h". Here, impunity leverages the capabilities of the sister Pint library: however,
the Pint functionalities are called only once at definition time, and not at runtime (i.e. every time
the function is executed) resulting in a tremendous gain in performance. 