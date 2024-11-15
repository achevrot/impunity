from typing import Annotated, Any

import quantities as pq

import numpy as np

rng = np.random.default_rng()

a: Annotated[Any, "meters"] = rng.random(100000) * pq.m
b: Annotated[Any, "seconds"] = rng.random(100000) * pq.s


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
    x.units = pq.m
    y.units = pq.s
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
