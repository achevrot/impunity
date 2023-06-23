# impunity

[![tests](https://github.com/achevrot/impunity/actions/workflows/run-tests.yml/badge.svg)](https://github.com/achevrot/impunity/actions/workflows/run-tests.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/achevrot/impunity.svg)](https://codecov.io/gh/achevrot/impunity)
![License](https://img.shields.io/pypi/l/impunity.svg) [![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy.readthedocs.io/) [![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

**impunity** is a Python library consisting of **a single decorator** function designed to ensure consistency of physical quantities. Compared to other libraries (pint, etc.), it has **a minimal overhead on performance** because physical units are only manipulated through static analysis and disappear at runtime.

impunity is based on Python “flexible variable and function annotations” ([PEP 593](https://peps.python.org/pep-0593/)) and checks consistency between variables and arguments of functions. If physical units are consistent, impunity rewrites the code by automatically applying conversions in the code of the function.

impunity is compatible with regular type annotations, and functions decorated with impunity remain compatible with other static analysis tools and type checkers like [mypy](https://mypy.readthedocs.io/).

In most situations, impunity will only perform minimal sanity checks on your code at import time and not edit anything.

## Installation

**impunity** is available on pip (and soon conda):

```sh
pip install impunity
```

For development purposes, clone the repository and use poetry:

```sh
git clone --depth=1 https://github.com/achevrot/impunity
cd impunity
poetry install
```

## Usage

Full documentation available at [website]()

- The most simple usage consists of using units placed as annotations: code is checked and rewritten if need be.

  ```python
  from impunity import impunity

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
  ```

- The check fails if units are inconsistent:

  ```python
  @impunity
  def inconsistent_units():
      temperatures: "K" = np.arange(0, 100, 10)
      duration: "s" = 6000
      return speed(temperatures, duration)

  # Warning: "K" is not compatible with "m"

- Only check for consistency, do not attempt to rewrite the code:

  ```python
  @impunity(rewrite=False)  # only check for consistency
  def regular_conversion():
      pass

  @impunity(rewrite="output.log")  # check code output in an external file
  def regular_conversion():
      pass
  ```

## Compatibility with type checkers

Types can be used with the `Annotated` keyword, which carries

```python
from typing import Annotation
import numpy.types as npt

feet_array = Annotated[npt.ndarray[np.float64], "ft"]
altitudes: feet_array = np.arange(0, 1000, 100)
```

**impunity** is implemented and typed with `Annotated` keywords.

## Tests

Tests are supported by the unittest package.

Because AST manipulation can be tricky, continuous integration is ensured by Github Actions for:

- Linux, MacOS and Windows;
- all versions of Python since 3.8

## Why impunity?

We were searching for a pun with physical units. Things converged on `im-pun-unit-y`.
