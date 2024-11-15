from typing import Annotated, Any

from numericalunits import hour, m, s

import numpy as np

rng = np.random.default_rng()

a: Annotated[Any, "meters"] = rng.random(100000) * m
b: Annotated[Any, "hours"] = rng.random(100000) * hour


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
    x = x / m
    y = y / s
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
