from typing import Annotated, Any

from astropy import units as u

import numpy as np

rng = np.random.default_rng()

a: Annotated[Any, "meters"] = rng.random(100000) * u.m
b: Annotated[Any, "hours"] = rng.random(100000) * u.h


@u.quantity_input(x=u.m, y=u.s)
def g(x, y):
    return x / y


if __name__ == "__main__":
    import time
    import timeit

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
