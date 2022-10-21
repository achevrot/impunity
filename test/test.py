import pytest
from super_couscous import check_units

m = int


@check_units
def f1() -> str:
    a: "m" = 2
    b = 4
    return a, b


def test_unit() -> str:
    a, b = f1()
    assert a == b


# %%
