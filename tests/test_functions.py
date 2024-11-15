from __future__ import annotations

import unittest
from typing import Any, Tuple

from typing_extensions import Annotated

import numpy as np
from impunity import impunity
from numpy import npt

from .sample_module import (
    speed_altitude_to_test,
    speed_to_test,
    speed_with_annotated_to_test,
)

m = Annotated[Any, "m"]
K = Annotated[Any, "K"]
ft = Annotated[Any, "ft"]
s = Annotated[Any, "s"]
cm = Annotated[Any, "cm"]
Pa = Annotated[Any, "Pa"]
kts = Annotated[Any, "kts"]
dimensionless = Annotated[Any, "dimensionless"]

STRATOSPHERE_TEMP: Annotated[float, "K"] = 216.65

# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------


@impunity
def atmosphere(
    h: Annotated[Any, "m"],
) -> Tuple[
    Annotated[Any, "Pa"],
    Annotated[Any, "kg * m^-3"],
    Annotated[Any, "K"],
]:
    """Pressure of ISA atmosphere

    :param h: the altitude (by default in meters), :math:`0 < h < 84852`
        (will be clipped when outside range, integer input allowed)

    :return: a tuple (pressure, density, temperature)

    """
    temp: Annotated[Any, "K"] = 288.15 - 0.0065 * h
    den: Annotated[Any, "kg * m^-3"] = 10
    press: Annotated[Any, "Pa"] = 10
    return press, den, temp


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
def temperature_3(altitude_m: "m") -> Annotated[Any, "celsius"]:
    temp = temperature(altitude_m)
    temp2: Annotated[Any, "celsius"] = temp
    return temp2


@impunity
def tas2mach(
    tas: Annotated[Any, "kts"], h: Annotated[Any, "ft"]
) -> Annotated[Any, "dimensionless"]:
    """
    :param tas: True Air Speed, (by default in kts)
    :param h: altitude, (by default in ft)

    :return: Mach number (dimensionless)
    """
    a: Annotated[Any, "m/s"] = 343
    M: Annotated[Any, "dimensionless"] = tas / a
    return M


class Functions(unittest.TestCase):
    @impunity
    def test_base(self) -> None:
        alt_m: "m" = 1000
        temp = temperature(alt_m)
        self.assertAlmostEqual(temp, 281.65, delta=1e-1)

    @impunity
    def test_base_cm(self) -> None:
        alt_m: "m" = 1000
        temp = temperature(alt_m)
        self.assertAlmostEqual(temp, 281.65, delta=1e-1)

        alt_cm: "cm" = 100000
        temp = temperature(alt_cm)
        self.assertAlmostEqual(temp, 281.65, delta=1e-1)

    @impunity
    def test_2_params(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 1000
        temp_m = temperature_2(alt_m, alt_ft)
        self.assertAlmostEqual(temp_m[0], 281.65, delta=1e-1)

    @impunity
    def test_2_params_expansion(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 1000
        temp_m, temp_ft = temperature_2(alt_m, alt_ft)
        self.assertAlmostEqual(temp_m, 281.65, delta=1e-1)
        self.assertAlmostEqual(temp_ft, 286.17, delta=1e-1)

    @impunity
    def test_different_units(self) -> None:
        alt_ft: "ft" = 1000
        temp = temperature(alt_ft)
        # TODO: radian / celsius
        self.assertAlmostEqual(temp, 286.17, delta=1e-1)

    @impunity
    def test_weird_signature(self) -> None:
        alt_ft: "ft" = 1000
        press, density, temp = atmosphere(alt_ft)

    @impunity
    def test_binOp(self) -> None:
        alt_ft: "ft" = 1000
        temp = temperature(alt_ft * 3)
        self.assertAlmostEqual(temp, 282.21, delta=1e-1)

    @impunity
    def test_call_multi_args(self) -> None:
        alt_m: "m" = 1000
        tas: "kts" = 200
        tas2mach(tas, alt_m)

    def test_call_np(self) -> None:
        @impunity
        def test_call_np(h: "m") -> "K":
            temp_0: "K" = 288.15
            c: Annotated[Any, "K/m"] = 0.0065
            temp: "K" = np.maximum(
                temp_0 - c * h,
                216.65,
            )
            return temp

        m_res: "m" = 11000
        res = test_call_np(m_res)
        self.assertAlmostEqual(res, 216.65, delta=1e-1)

    def test_using_globals(self) -> None:
        @impunity
        def test_using_globals(h: "m") -> "K":
            temp_0: "K" = 288.15
            c: Annotated[Any, "K/m"] = 0.0065
            e = STRATOSPHERE_TEMP
            temp: "K" = np.maximum(
                temp_0 - c * h,
                e,
            )
            return temp

        m_res: "m" = 11000
        res = test_using_globals(m_res)
        self.assertAlmostEqual(res, STRATOSPHERE_TEMP, delta=1e-1)

    def test_empty_return(self) -> None:
        @impunity
        def test_empty_return(self):  # type: ignore
            return 0

        with self.assertLogs("impunity.visitor", level="INFO") as cm:
            impunity(test_empty_return)
        self.assertTrue(
            cm.output[0].endswith("Some return annotations are missing")
        )

    def test_return_convert(self) -> None:
        @impunity
        def test_return_convert() -> Annotated[Any, "ft"]:
            alt_ft: "ft" = 1000
            alt_m: "m" = alt_ft
            return alt_m

        self.assertAlmostEqual(test_return_convert(), 1000, delta=1e-2)

    def test_module(self) -> None:
        @impunity
        def test_module() -> Annotated[Any, "m/s"]:
            distance: "ft" = 1000
            duration: "s" = 1000
            return speed_to_test(distance, duration)

        self.assertAlmostEqual(test_module(), 0.305, delta=1e-2)

    @impunity
    def test_builtin(self) -> None:
        print(speed_to_test(1, 10))

    @impunity
    def test_keyword(self) -> None:
        d: "m" = 1000
        t: "s" = 1000
        a: "ft" = 1000

        res = speed_altitude_to_test(d, t, a)
        self.assertAlmostEqual(res, 417.17, delta=1e-2)
        res2 = speed_altitude_to_test(d, t)
        self.assertAlmostEqual(res2, 1, delta=1e-2)

    @impunity
    def test_conversion_with_module(self) -> None:
        # Using meters instead of Annotated[float, "m"]
        altitudes: Annotated[npt.ArrayLike, "meters"] = np.arange(0, 1000, 100)
        duration: Annotated[float, "min"] = 100
        result = speed_with_annotated_to_test(altitudes, duration)
        self.assertAlmostEqual(result[3], 0.05, delta=1e-2)


if __name__ == "__main__":
    unittest.main()
