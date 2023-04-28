import sys
import unittest
from typing import Any

from impunity import impunity

import numpy as np

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

global_alt: "m" = 1000


@impunity
def identity_m(h: Annotated[int, "m"]) -> Annotated[int, "m"]:
    return h


@impunity
def identity_ft(h: Annotated[int, "ft"]) -> Annotated[int, "ft"]:
    return h


class Assign(unittest.TestCase):
    @impunity
    def test_assign_same_unit(self) -> None:
        alt_m: "m" = 1000
        alt_m2: "m" = alt_m
        self.assertEqual(alt_m, alt_m2)

        global_copy: "m" = global_alt
        self.assertEqual(global_copy, global_alt)

    @impunity
    def test_assign_same_unit_annotated(self) -> None:
        alt_m: Annotated[float, "m"] = 1000
        alt_m2: Annotated[float, "m"] = alt_m
        assert alt_m == alt_m2

        global_copy: Annotated[float, "m"] = global_alt
        assert global_copy == global_alt

    @impunity
    def test_assign_compatible_unit(self) -> None:
        alt_m: "m" = 1000
        alt_ft: "ft" = alt_m
        self.assertAlmostEqual(alt_ft, 3280.84, delta=1e-2)

    def test_assign_incompatible_unit(self) -> None:
        def test_assign_incompatible_unit() -> None:
            alt_m: "m" = 1000
            alt_ft: "K" = alt_m
            self.assertEqual(alt_ft, 1000)

        with self.assertLogs("impunity.visitor", level="WARNING") as cm:
            impunity(test_assign_incompatible_unit)
        self.assertEqual(
            cm.output,
            [
                f"WARNING:impunity.visitor:In function {__name__}/"
                + "test_assign_incompatible_unit: Assignement "
                + "expected unit K but received incompatible unit m."
            ],
        )

    @impunity
    def test_assign_wo_annotation(self) -> None:
        density_troposphere = np.maximum(1500, 6210)  # return None unit
        density: "Pa" = density_troposphere * np.exp(0)
        self.assertEqual(density, 6210)

    @impunity
    def test_no_unit(self) -> None:
        no_unit = 0
        self.assertEqual(identity_m(0), 0)
        self.assertEqual(identity_m(no_unit), 0)

    def test_no_unit_conflict(self) -> None:
        def test_no_unit_conflict() -> None:
            no_unit = 0
            identity_m(no_unit)
            identity_ft(no_unit)

        with self.assertLogs("impunity.visitor", level="WARNING") as cm:
            impunity(test_no_unit_conflict)
        self.assertEqual(
            cm.output,
            [
                "WARNING:impunity.visitor:The variable no_unit is not "
                + "annotated. Defaulted to dimensionless",
                "WARNING:impunity.visitor:The variable no_unit "
                + "is not annotated. Defaulted to dimensionless",
            ],
        )


if __name__ == "__main__":
    unittest.main()
