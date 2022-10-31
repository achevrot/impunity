from re import T
from typing import Any
import pytest
from super_couscous import check_units
import pint
from pitot import Q_
import numpy as np

m = K = ft = Any


# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------


def temperature(altitude_m: "m") -> "K":
    temp: pint.Quantity[Any] = np.maximum(288.15 - 0.0065 * altitude_m, 216.65)
    return temp


def temperature_2(altitude_m: "m", altitude_ft: "ft") -> "K":
    temp_m: pint.Quantity[Any] = np.maximum(
        288.15 - 0.0065 * altitude_m, 216.65
    )
    temp_ft: pint.Quantity[Any] = np.maximum(
        288.15 - 0.0065 * altitude_ft * 0.3048, 216.65
    )
    return temp_m, temp_ft


@check_units
def test_base():

    alt_m: "m" = 1000
    temp = temperature(alt_m)
    assert temp == pytest.approx(281.65, rel=1e-1)


def test_2_params():
    @check_units
    def test_function_call_2():

        alt_m: "m" = 1000
        alt_ft: "ft" = 1000
        temp_m, temp_ft = temperature_2(alt_m, alt_ft)
        assert temp_m == pytest.approx(281.65, rel=1e-1)
        assert temp_ft == pytest.approx(286.17, rel=1e-1)

    test_function_call_2()


@check_units
def test_different_units():
    alt_ft: "ft" = 1000
    temp = temperature(alt_ft)
    assert temp == pytest.approx(286.17, rel=1e-1)


def test_binOp():
    @check_units
    def test_bin_function_call():
        alt_ft: "ft" = 1000
        temp = temperature(alt_ft * 3)
        assert temp == pytest.approx(286.17, rel=1e-1)

    test_bin_function_call()


@check_units
def test_wrong_units():
    with pytest.raises(pint.errors.DimensionalityError):
        alt_ft: "K" = 1000
        temperature(alt_ft)
