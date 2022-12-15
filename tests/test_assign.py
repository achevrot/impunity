from typing import Any, Annotated

import pint
import pytest

import numpy as np
from impunity import impunity

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
def test_assign_same_unit() -> None:
    alt_m: "m" = 1000
    alt_m2: "m" = alt_m
    assert alt_m == alt_m2

    global_copy: "m" = global_alt
    assert global_copy == global_alt


@impunity
def test_assign_same_unit_annotated() -> None:
    alt_m: Annotated[float, "m"] = 1000
    alt_m2: Annotated[float, "m"] = alt_m
    assert alt_m == alt_m2

    global_copy: Annotated[float, "m"] = global_alt
    assert global_copy == global_alt


@impunity
def test_assign_compatible_unit() -> None:
    alt_m: "m" = 1000
    alt_ft: "ft" = alt_m
    assert alt_ft == pytest.approx(3280.84, rel=1e-2)

    # test fails with this one
    # global_ft: "ft" = global_alt
    # assert global_ft == pytest.approx(3280.84, rel=1e-2)


@impunity
def test_assign_incompatible_unit() -> None:
    with pytest.raises(pint.errors.DimensionalityError):
        alt_m: "m" = 1000
        invalid: "K" = alt_m  # noqa: F841


@impunity
def test_assign_wo_annotation() -> None:
    density_troposphere = np.maximum(1500, 6210)  # return None unit
    density: "Pa" = density_troposphere * np.exp(0)
    assert density == 6210
