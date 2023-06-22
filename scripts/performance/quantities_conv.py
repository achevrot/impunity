import quantities as pq
from typing import Annotated, Any
import numpy as np

a: Annotated[Any, "meters"] = np.random.rand(100000) * pq.m
b: Annotated[Any, "hours"] = np.random.rand(100000) * pq.h


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
    x.units = pq.m
    y.units = pq.s
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
