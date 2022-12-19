import unittest
from typing import Any

from impunity import impunity

m = Any
K = Any
ft = Any


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
