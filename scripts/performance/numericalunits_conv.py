from numericalunits import hour, m, s
from typing import Annotated, Any
import numpy as np

a: Annotated[Any, "meters"] = np.random.rand(100000) * m
b: Annotated[Any, "hours"] = np.random.rand(100000) * hour


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
    x = x / m
    y = y / s
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
