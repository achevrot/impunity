# %%


from typing import Annotated, Any
import numpy as np

a: Annotated[Any, "meters"] = np.random.rand(100000)
b: Annotated[Any, "hours"] = np.random.rand(100000) / 3600


def g(
    x: Annotated[Any, "meters"], y: Annotated[Any, "seconds"]
) -> Annotated[Any, "m/s"]:
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
# %%
