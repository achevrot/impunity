from typing import Any

import pytest

from impunity import impunity

m = K = ft = Any


@impunity
def test_various_units():
    alt_1: "m" = 1000
    alt_2: "ft" = 350
    temp: "K" = 120
    result: "m / K" = (alt_1 + alt_2) * 25 / temp
    assert result == pytest.approx(230.55, rel=1e-2)


@impunity
def test_convert_units():
    alt_m: "m" = 1000
    alt_ft: "ft" = 2000
    alt_m2: "m" = 3000
    result: "m" = alt_m + alt_ft + alt_m2
    assert result == pytest.approx(4609.6, rel=1e-2)


@impunity
def test_dimless_var():
    # TODO what do you really expect here?
    alt_m: "m" = 1000
    alt_ft: "ft" = 2000
    alt_m2: "m" = 3000
    alt = alt_m + alt_ft + alt_m2
    result = alt * 3
    assert result == pytest.approx(4609.6 * 3, rel=1e-2)


@impunity
def test_operation():
    alt_m: "m" = 1000
    alt_ft: "ft" = 2000
    alt_m2: "m" = 3000
    # TODO explain what you mean?
    _, result_2 = (alt_m + alt_ft + alt_m2, alt_m + alt_ft + alt_m2)
    assert result_2 == pytest.approx(4609.6, rel=1e-2)
