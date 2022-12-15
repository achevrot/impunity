from typing import Any
import pytest

from impunity import impunity

m = K = ft = Any


@impunity
def test_convert_units():
    alt_m: "m" = 1000
    alt_ft: "ft" = 2000
    alt_m2: "m" = 3000
    result: "m" = alt_m + alt_ft + alt_m2
    assert result == pytest.approx(4609.6, rel=1e-2)


@impunity(rewrite=False)
def test_convert_units_unchecked():
    alt_m: "m" = 1000
    alt_ft: "ft" = 2000
    alt_m2: "m" = 3000
    result: "m" = alt_m + alt_ft + alt_m2
    assert result != pytest.approx(4609.6, rel=1e-2)
