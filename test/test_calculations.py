from typing import Any
import pytest
from impunity.wrapper import impunity

m = K = ft = Any


def test_mixed_units():
    @impunity
    def test_mixed_units():
        alt_1: "m" = 1000
        alt_2: "ft" = 350
        temp: "K" = 120
        result: "m / K" = (alt_1 + alt_2) * 25 / temp
        assert result == pytest.approx(230.55, rel=1e-2)

    test_mixed_units()


def test_add_operation():
    @impunity
    def test_operation():
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        result: "m" = alt_m + alt_ft + alt_m2
        assert result == pytest.approx(4609.6, rel=1e-2)

    test_operation()


def test_dimless_var():
    @impunity
    def test_dimless_var():
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        alt = alt_m + alt_ft + alt_m2
        result = alt * 3
        assert result == pytest.approx(4609.6 * 3, rel=1e-2)

    test_dimless_var()


def test_list_operation():
    @impunity
    def test_operation():
        alt_m: "m" = 1000
        alt_ft: "ft" = 2000
        alt_m2: "m" = 3000
        _, result_2 = (alt_m + alt_ft + alt_m2, alt_m + alt_ft + alt_m2)
        assert result_2 == pytest.approx(4609.6, rel=1e-2)

    test_operation()
