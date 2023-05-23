Decorator Parameters
====================

The **Impunity** decorator provides additional parameters that allow for
more flexibility and control over the unit coherence checking process.
These parameters can be passed to the decorator to modify its behavior
according to specific requirements.

ignore
------
The `ignore` parameter allows you to specify names of
functions or methods that should be ignored during unit
coherence checking. When a decorated class contains functions
or methods that you want to exclude from the coherence checking
process, you can use the `ignore` parameter to specify those
functions or methods.

.. code-block:: python

    from impunity import impunity

    @impunity
    class MyClass:

    def calculate_velocity(distance: "meters", time: "seconds") -> "m/s":
        return distance / time

    @impunity(ignore=True)
    def function_to_ignore():
        # This function will be ignored during unit coherence checking
        pass

In this example, the `calculate_velocity`
function is check thanks to the `@impunity` decorator of the class. 
On the other hand, `@impunity(ignore=True)` ensures that the
`function_to_ignore` is excluded from unit coherence checking,
allowing you to selectively ignore specific functions or methods.

rewrite
-------

The `rewrite` parameter enables you to specify a file path where the
rewritten functions will be saved. When this parameter is provided,
the modified functions, with the necessary unit conversions added,
will be written to the specified file.

.. code-block:: python

    from impunity import impunity

    @impunity(rewrite="path/to/rewritten_functions.py")
    def calculate_velocity(distance: float, time: float) -> float:
        return distance / time

In this example, the `calculate_velocity`
function is decorated with `@impunity`
and the `rewrite` parameter is set to `"path/to/rewritten_functions.py"`.
After the coherence checking process, the modified function,
with the necessary unit conversions added, will be saved to 
the specified file.

These rewritten functions can be further utilized in your codebase, 
allowing you to work with coherent units seamlessly.

Conclusion
----------

The `ignore` and `rewrite` parameters provided by the **Impunity** decorator 
offer additional flexibility and control over the unit coherence checking 
process. By specifying functions or methods to ignore and providing a file 
path for rewritten functions, you can customize the behavior of the decorator 
according to your specific needs.


Please note that the `ignore` and `rewrite` parameters are optional, 
and you can choose to use them based on your requirements and preferences.
