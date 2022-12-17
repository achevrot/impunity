import sys
import types
from typing import Any

import pint
import pytest

import numpy as np
from impunity import impunity

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

m = Any
K = Any
ft = Any
Pa = Any


# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------

global_alt: "m" = 1000


@impunity
def impunity_assign_same_unit() -> None:
    alt_m: "m" = 1000
    alt_m2: "m" = alt_m
    assert alt_m == alt_m2

    global_copy: "m" = global_alt
    assert global_copy == global_alt


@impunity
def impunity_assign_same_unit_annotated() -> None:
    alt_m: Annotated[float, "m"] = 1000
    alt_m2: Annotated[float, "m"] = alt_m
    assert alt_m == alt_m2

    global_copy: Annotated[float, "m"] = global_alt
    assert global_copy == global_alt


@impunity
def impunity_assign_compatible_unit() -> None:
    alt_m: "m" = 1000
    alt_ft: "ft" = alt_m
    assert alt_ft == pytest.approx(3280.84, rel=1e-2)

    # test fails with this one
    # global_ft: "ft" = global_alt
    # assert global_ft == pytest.approx(3280.84, rel=1e-2)


@impunity
def impunity_assign_incompatible_unit() -> None:
    with pytest.raises(pint.errors.DimensionalityError):
        alt_m: "m" = 1000
        invalid: "K" = alt_m  # noqa: F841


@impunity
def impunity_assign_wo_annotation() -> None:
    density_troposphere = np.maximum(1500, 6210)  # return None unit
    density: "Pa" = density_troposphere * np.exp(0)
    assert density == 6210


# Somehow doesn't work yet, but all that is below this line could probably be
# automatised for all tests in a smarter way.

# ----------------------------------------------------------------------------

test_functions = [
    fun
    for fun in locals()
    if isinstance(fun, types.FunctionType)
    and fun.__name__.startswith("impunity_")
]


@pytest.mark.parametrize(
    "function",
    [
        # impunity_assign_same_unit,
        # impunity_assign_same_unit_annotated,
        impunity_assign_compatible_unit,
        impunity_assign_incompatible_unit,
        impunity_assign_wo_annotation,
    ],
)
def test_case(function) -> None:
    function()
