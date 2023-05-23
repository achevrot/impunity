Guidelines for Choosing Appropriate Units
========================================

Choosing appropriate units is crucial for ensuring the accuracy and coherence of
physical quantities in your code. **Impunity** leverages the functionality of
the Pint library to provide unit coherence and conversions. As a consequence,
**only units supported by the Pint library can be used with Impunity**. 
Follow these guidelines to select suitable units for your code:

Consistency
-----------

Maintain consistency throughout your codebase by using the same units for similar quantities. 
This consistency enhances code readability and reduces the chances of introducing errors. 
For example, if you're working with lengths, consistently use meters or kilometers 
instead of mixing different units like feet or inches.

Base Units
----------

Prefer using base units whenever possible. Base units are fundamental units of measurement 
that are defined independently of other units. Examples of base units include meters for length, 
seconds for time, and kilograms for mass. Using base units simplifies calculations and conversions.

Unit Conversions
----------------

Whenever needed, **Impunity** will use the power of the Pint library to perform unit conversions effortlessly.
Pint provides a comprehensive set of predefined units and allows you to define 
custom units as well. This ensures consistency and accuracy when working 
with physical quantities.

**FUTURE WORK : Define the user-defined set of unit to use in Impunity**

Physical Context
----------------

Consider the physical context in which your code operates. 
Choose units that are relevant and meaningful to the problem domain. 
For example, when working with astronomical distances, using astronomical units (AU) 
or light-years might be more appropriate than meters or kilometers.

Readability
-----------

Opt for units that improve code readability and comprehension. 
Choose units that are widely recognized and commonly used in the field. 
Additionally, consider using unit symbols or abbreviations that are easily 
understood by domain experts.

Documentation
-------------

Document the units used in your code to provide clarity and avoid confusion. 
Clearly specify the units for variables, function parameters, and return types 
in your code documentation. This helps other developers understand the expected 
units and promotes correct usage of your library.

By following these guidelines, you can ensure the appropriate choice of units in your code, 
enhance the clarity of your codebase, and maintain coherence and accuracy in physical quantities.
