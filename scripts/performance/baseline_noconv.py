# %%
from typing import Annotated, Any

import numpy as np

a: Annotated[Any, "meters"] = np.random.rand(100000)
b: Annotated[Any, "seconds"] = np.random.rand(100000)


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
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

# %%
