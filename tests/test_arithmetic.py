import unittest
from typing import Any

from typing_extensions import Annotated

import numpy as np
from impunity import impunity

m = Annotated[Any, "m"]
K = Annotated[Any, "K"]
ft = Annotated[Any, "ft"]
cm = Annotated[Any, "cm"]
Pa = Annotated[Any, "Pa"]
kts = Annotated[Any, "kts"]
degC = Annotated[Any, "degC"]
degF = Annotated[Any, "degF"]
dimensionless = Annotated[Any, "dimensionless"]


class Arithmetic(unittest.TestCase):
    @impunity
    def test_various_units(self) -> None:
        alt_1: Annotated[Any, "m"] = 1000
        alt_2: Annotated[Any, "ft"] = 350
        temp: "K" = 120
        result: "m / K" = (alt_1 + alt_2) * 25 / temp  # type: ignore

        self.assertAlmostEqual(result, 230.55, delta=1e-2)

    @impunity
    def test_power(self) -> None:
        dist: Annotated[Any, "m"] = 1000
        speed: Annotated[Any, "m/s"] = 350
        time: Annotated[Any, "s"] = 120
        result: Annotated[Any, "kts"] = (dist * speed / time) ** (1 / 2)

        self.assertNotAlmostEqual(result, 54, delta=1e-2)

    @impunity
    def test_convert_units(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        result: "m" = alt_m + alt_ft + alt_m2

        self.assertAlmostEqual(result, 4609.6, delta=1e-2)

    @impunity
    def test_temperatures(self) -> None:
        temp_C: "degC" = 1000
        temp_K: "K" = temp_C
        temp_F: "degF" = temp_C

        self.assertAlmostEqual(temp_K, 1273.15, delta=1e-2)
        self.assertAlmostEqual(temp_F, 1832, delta=1e-2)

    @impunity
    def test_dimless_var(self) -> None:
        # TODO what do you really expect here?
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        alt = alt_m + alt_ft + alt_m2
        result = alt * 3

        self.assertAlmostEqual(result, 4609.6 * 3, delta=1e-2)

    @impunity
    def test_operation(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        _, result_2 = (alt_m + alt_ft + alt_m2, alt_m + alt_ft + alt_m2)

        self.assertAlmostEqual(result_2, 4609.6, delta=1e-2)

    @impunity
    def test_tuple(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_cm: "cm" = 3000
        alt_m2, alt_ft2, alt_cm2 = (alt_m, alt_ft, alt_cm)
        _, result_2 = (alt_m2 + alt_ft2 + alt_cm2, alt_m2 + alt_ft2 + alt_cm2)

        self.assertAlmostEqual(result_2, 1639.6, delta=1e-2)

    def test_operation_list(self) -> None:
        def test_operation_list() -> None:
            alt_m: "m" = [1000, 2000, 3000]
            alt_ft: "ft" = alt_m
            res = alt_ft[0] + alt_ft[1] + alt_ft[2]
            self.assertAlmostEqual(res, 6000, delta=1e-2)

        with self.assertLogs("impunity.visitor", level="WARNING") as cm:
            impunity(test_operation_list)

        self.assertTrue(cm.output[0].endswith("(but numpy arrays are)"))

    @impunity
    def test_operation_array(self) -> None:
        alt_m: "m" = np.array([1000, 2000, 3000])
        alt_ft: "ft" = alt_m
        res = alt_ft[0] + alt_ft[1] + alt_ft[2]
        self.assertAlmostEqual(res, 19685.039, delta=1e-2)

    @impunity
    def test_value_BinOp(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        res_1 = alt_m + alt_ft + alt_m2
        self.assertAlmostEqual(res_1, 4609.6, delta=1e-2)
        res_2: "ft" = 3000 + alt_m
        self.assertAlmostEqual(res_2, 13123.36, delta=1e-2)

    def test_addition_wrong(self) -> None:
        def test_addition_wrong() -> None:
            alt_m: "m" = 1000
            alt_ft: "K" = 2000
            res = alt_m + alt_ft
            self.assertEqual(res, 3000)

        with self.assertLogs("impunity.visitor", level="WARNING") as cm:
            impunity(test_addition_wrong)

        self.assertTrue(cm.output[0].endswith("Fallback to dimensionless"))

    @impunity
    def test_ternary_ok(self) -> None:
        alt_ft1: "ft" = 1000
        alt_ft2: "ft" = 2000
        res: "ft" = alt_ft1 if alt_ft1 > 2000 else alt_ft2
        self.assertAlmostEqual(res, 2000, delta=1e-2)

    def test_ternary_ko(self) -> None:
        def test_ternary_ko() -> None:
            alt_ft1: "m" = 1000
            alt_ft2: "ft" = 2000
            res: "ft" = alt_ft1 if alt_ft1 > 2000 else alt_ft2
            self.assertAlmostEqual(res, 2000, delta=1e-2)

        with self.assertLogs("impunity.visitor", level="WARNING") as cm:
            impunity(test_ternary_ko)

        self.assertTrue(
            cm.output[0].endswith("Ternary operator with mixed units.")
        )


if __name__ == "__main__":
    unittest.main()
