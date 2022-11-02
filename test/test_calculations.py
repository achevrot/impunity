from typing import Any
import pytest
from super_couscous import check_units
import pint
from pitot import Q_
import numpy as np

m = K = ft = Any


def test_mixed_units():
    @check_units
    def test_mixed_units():
        alt_1: "m" = 1000
        alt_2: "ft" = 350
        temp: "K" = 120
        result: "m / K" = (alt_1 + alt_2) * 25 / temp

        assert result == pytest.approx(209.22, rel=1e-2)

    test_mixed_units()
