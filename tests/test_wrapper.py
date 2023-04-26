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


@impunity
class WrappedClass:
    class_alt: Annotated[Any, "m"] = 1000

    def f(self, h: Annotated[Any, "m"]) -> Annotated[Any, "ft"]:
        alt_ft: Annotated[Any, "ft"] = h
        return alt_ft


class Wrapper(unittest.TestCase):
    @impunity
    def test_convert_units(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        result: "m" = alt_m + alt_ft + alt_m2
        self.assertAlmostEqual(result, 4609.6, delta=1e-2)

    @impunity(rewrite=False)
    def test_convert_units_unchecked(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        result: "m" = alt_m + alt_ft + alt_m2
        self.assertAlmostEqual(result, 6000, delta=1e-2)

    @impunity(ignore=True)
    def test_wrapper_ignore(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = alt_m
        self.assertEqual(alt_ft, 1000)

    @impunity(rewrite="log.log")
    def test_rewrite_relative(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = alt_m
        self.assertAlmostEqual(alt_ft, 3280.83, delta=1e-2)

    def test_class(self) -> None:
        c = WrappedClass()
        self.assertAlmostEqual(c.f(c.class_alt), 3280.83, delta=1e-2)

    def test_unknown_annotation(self) -> None:
        @impunity
        def weird_f(h: int, h_2: "m") -> "m":
            res: "ft" = h + h_2
            return res

        res = weird_f(1000, 1000)
        self.assertAlmostEqual(res, 6561.67, delta=1e-2)

        # TODO : Adding check for the warning


if __name__ == "__main__":
    unittest.main()
