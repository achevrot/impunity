import sys
import unittest
from typing import Any

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


class Arithmetic(unittest.TestCase):
    @impunity
    def test_various_units(self) -> None:
        alt_1: "m" = 1000
        alt_2: "ft" = 350
        temp: "K" = 120
        result: "m / K" = (alt_1 + alt_2) * 25 / temp  # type: ignore

        self.assertAlmostEqual(result, 230.55, delta=1e-2)

    @impunity
    def test_convert_units(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        result: "m" = alt_m + alt_ft + alt_m2

        self.assertAlmostEqual(result, 4609.6, delta=1e-2)

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

        self.assertEqual(
            cm.output,
            [
                "WARNING:impunity.visitor:In function tests.test_arithmetic"
                + "/test_addition_wrong: Type m and K are not compatible. "
                + "Defaulted to dimensionless"
            ],
        )


if __name__ == "__main__":
    unittest.main()
