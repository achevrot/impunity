import sys
import unittest
from typing import Any, Tuple

import numpy as np
from impunity import impunity

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

m = Annotated[Any, "m"]
K = Annotated[Any, "K"]
ft = Annotated[Any, "ft"]
cm = Annotated[Any, "cm"]
Pa = Annotated[Any, "Pa"]
kts = Annotated[Any, "kts"]
dimensionless = Annotated[Any, "dimensionless"]

# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------


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

    # def test_weird_signature(self)-> None:
    #     @impunity
    #     def test_weird_signature(self)-> None:
    #         alt_ft: "ft" = 1000
    #         press, density, temp = isa.atmosphere(alt_ft)

    #     test_weird_signature()

    @impunity
    def test_binOp(self) -> None:
        alt_ft: "ft" = 1000
        temp = temperature(alt_ft * 3)
        self.assertAlmostEqual(temp, 282.21, delta=1e-1)

    # def test_call_multi_args(self)-> None:
    #     @impunity
    #     def test_call_multi_args(self)-> None:
    #         alt_m: "m" = 1000
    #         tas: "kts" = 200
    #         res: "dimensionless" = aero.tas2mach(tas, alt_m)

    #     test_call_multi_args()

    # def test_call_np(self)-> None:
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
    #     assert res == pytest.approx(isa.STRATOSPHERE_TEMP, delta=1e-1)

    # def test_using_globals(self)-> None:
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
    #     assert res == pytest.approx(isa.STRATOSPHERE_TEMP, delta=1e-1)

    # @impunity
    # def test_wrong_units(self) -> None:
    #     with self.assertLogs(_log):
    #         alt_ft: "K" = 1000
    #         temperature(alt_ft)

    # @impunity
    # def test_wrong_units1(self) -> None:
    #     alt_ft: "ft" = 1000
    #     with self.assertLogs() as captured:
    #         res: "ft" = temperature(alt_ft)  # noqa: F841
    #     self.assertEqual(len(captured.records), 1)


if __name__ == "__main__":
    unittest.main()
