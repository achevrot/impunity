from typing import Any
import pytest
from super_couscous import check_units
import pint
from pitot import Q_
import numpy as np

m = K = ft = Any


# -----------------------
# du : different units
# wu : wrong units
# bin : Binary operator in func call
# -----------------------


@check_units
def test_base():

    alt_m: "m" = 1000
    alt_m2: "m" = alt_m
    assert alt_m == alt_m2


def test_different_units():
    @check_units
    def test_different_units():

        alt_m: "m" = 1000
        alt_ft: "ft" = alt_m
        assert alt_m != alt_ft

    test_different_units()


def test_wrong_units():
    @check_units
    def test_wrong_units():

        alt_m: "m" = 1000
        with pytest.raises(pint.errors.DimensionalityError):
            alt_K: "K" = alt_m

    test_wrong_units()


def main():
    test_wrong_units()


if __name__ == "__main__":
    main()
