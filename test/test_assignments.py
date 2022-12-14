from typing import Any
import pytest
from impunity.wrapper import impunity
import pint
import numpy as np

m = K = ft = Pa = Any


# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------


def test_base():
    @impunity
    def test_base():
        alt_m: "m" = 1000
        alt_m2: "m" = alt_m
        assert alt_m == alt_m2

    test_base()


def test_different_units():
    @impunity
    def test_different_units():

        alt_m: "m" = 1000
        alt_ft: "ft" = alt_m
        # assert alt_m == 1000
        assert alt_ft == pytest.approx(3280.84, rel=1e-2)

    test_different_units()


def test_wrong_units():
    @impunity
    def test_wrong_units():
        with pytest.raises(pint.errors.DimensionalityError):
            alt_m: "m" = 1000
            alt_K: "K" = alt_m

    test_wrong_units()


def test_assign_wo_annotation():
    @impunity
    def test_assign_wo_annotation():
        density_troposphere = np.maximum(1500, 6210)  # return None unit
        density: "Pa" = density_troposphere * np.exp(0)
        assert density == 6210

    test_assign_wo_annotation()


def main():
    test_different_units()


if __name__ == "__main__":
    main()
