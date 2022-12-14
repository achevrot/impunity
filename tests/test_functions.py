from typing import Any, Tuple

import pint
import pytest

import numpy as np
from impunity import impunity

m = K = ft = cm = Pa = kts = dimensionless = Any

# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------

# TODO ça peut valoir le coup de mettre ces fonctions d'abord dans un config.py
# puis après de faire un autre fichier de test qui vérifie les imports

@impunity
def temperature(altitude_m: "m") -> "K":
    temp: "K" = np.maximum(288.15 - 0.0065 * altitude_m, 216.65)
    return temp


@impunity
def temperature_2(altitude_m: "m", altitude_ft: "ft") -> Tuple["K", "K"]:
    temp_m: "K" = np.maximum(288.15 - 0.0065 * altitude_m, 216.65)
    temp_ft: "K" = np.maximum(288.15 - 0.0065 * altitude_ft * 0.3048, 216.65)
    return temp_m, temp_ft


@impunity
def test_base():

    alt_m: "m" = 1000
    temp = temperature(alt_m)
    assert temp == pytest.approx(281.65, rel=1e-1)


@impunity
def test_base_cm():

    alt_m: "m" = 1000
    temp = temperature(alt_m)
    assert temp == pytest.approx(281.65, rel=1e-1)

    alt_cm: "cm" = 100000
    temp = temperature(alt_cm)
    assert temp == pytest.approx(281.65, rel=1e-1)


@impunity
def test_2_params():

    alt_m: "m" = 1000
    alt_ft: "ft" = 1000
    temp_m = temperature_2(alt_m, alt_ft)
    assert temp_m[0] == pytest.approx(281.65, rel=1e-1)


@impunity
def test_2_params():

    alt_m: "m" = 1000
    alt_ft: "ft" = 1000
    temp_ft, temp_m = temperature_2(alt_m, alt_ft)
    assert temp_m == pytest.approx(281.65, rel=1e-1)
    assert temp_ft == pytest.approx(286.17, rel=1e-1)


@impunity
def test_different_units():
    alt_ft: "ft" = 1000
    temp = temperature(alt_ft)
    assert temp == pytest.approx(286.17, rel=1e-1)


# def test_weird_signature():
#     @impunity
#     def test_weird_signature():
#         alt_ft: "ft" = 1000
#         press, density, temp = isa.atmosphere(alt_ft)

#     test_weird_signature()


@impunity
def test_binOp():
    alt_ft: "ft" = 1000
    temp = temperature(alt_ft * 3)
    assert temp == pytest.approx(286.17, rel=1e-1)


# def test_call_multi_args():
#     @impunity
#     def test_call_multi_args():
#         alt_m: "m" = 1000
#         tas: "kts" = 200
#         res: "dimensionless" = aero.tas2mach(tas, alt_m)

#     test_call_multi_args()


# def test_call_np():
#     @impunity
#     def test_call_np(h: "m") -> "K":

#         temp_0: "K" = 288.15
#         c: "K/m" = 0.0065
#         temp: "K" = np.maximum(
#             temp_0 - c * h,
#             216.65,
#         )
#         return temp

#     m: "m" = 11000
#     res = test_call_np(m)
#     assert res == pytest.approx(isa.STRATOSPHERE_TEMP, rel=1e-1)


# def test_using_globals():
#     @impunity
#     def test_using_globals(h: "m") -> "K":

#         temp_0: "K" = 288.15
#         c: "K/m" = 0.0065
#         e = isa.STRATOSPHERE_TEMP
#         temp: "K" = np.maximum(
#             temp_0 - c * h,
#             e,
#         )
#         return temp

#     m: "m" = 11000
#     res = test_using_globals(m)
#     assert res == pytest.approx(isa.STRATOSPHERE_TEMP, rel=1e-1)


@impunity
def test_wrong_units():
    with pytest.raises(pint.errors.DimensionalityError):
        alt_ft: "K" = 1000
        temperature(alt_ft)


@impunity
def test_wrong_units1():
    alt_ft: "ft" = 1000
    with pytest.raises(pint.errors.DimensionalityError):
        res: "ft" = temperature(alt_ft)
