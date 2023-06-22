from astropy import units as u
from typing import Annotated, Any
import numpy as np

np.random.seed(0)

a: Annotated[Any, "meters"] = np.random.rand(100000) * u.m
b: Annotated[Any, "seconds"] = np.random.rand(100000) * u.s


@u.quantity_input(x=u.m, y=u.s)
def g(x, y):
    return x / y


if __name__ == "__main__":
    import timeit
    import time

    print(
        np.mean(
            timeit.repeat(
                "g(a,b)",
                globals=globals(),
                timer=time.process_time,
                repeat=300,
                number=10,
            )
        )
    )
