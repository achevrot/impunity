import unittest
from typing import Any

from impunity import impunity
from typing_extensions import Annotated

m = Annotated[Any, "m"]
K = Annotated[Any, "K"]
ft = Annotated[Any, "ft"]
cm = Annotated[Any, "cm"]
Pa = Annotated[Any, "Pa"]
kts = Annotated[Any, "kts"]
dimensionless = Annotated[Any, "dimensionless"]


@impunity(rewrite="log.txt")
class WrappedClass:
    class_alt: m = 1000

    def f(self, h: Annotated[Any, "m"]) -> Annotated[Any, "ft"]:
        alt_ft: Annotated[Any, "ft"] = h
        return alt_ft

    def double(self, h: Annotated[Any, "m"]) -> Annotated[Any, "m"]:
        x: Annotated[Any, "ft"] = h

        return x + x


@impunity(ignore_methods=True)
class WrappedIgnoreClass:
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
        def test_unknown_annotation(h: int, h_2: "ft") -> "m":
            res: "ft" = h + h_2
            res2: "m" = res
            return res2

        res = test_unknown_annotation(1000, 1000)
        self.assertAlmostEqual(res, 609.60, delta=1e-2)

    def test_class_method_ignore(self) -> None:
        c = WrappedIgnoreClass()
        self.assertAlmostEqual(c.f(c.class_alt), 1000, delta=1e-2)

    def test_check_nested_scope(self) -> None:
        c = WrappedClass()
        self.assertAlmostEqual(c.double(c.class_alt), 2000, delta=1e-2)

        # TODO : Adding check for the warning


if __name__ == "__main__":
    unittest.main()

# %%
