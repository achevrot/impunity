# %%


from typing import Annotated, Any

import pint

import numpy as np

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

a: Annotated[Any, "meters"] = Q_(np.random.rand(100000), "meter")
b: Annotated[Any, "seconds"] = Q_(np.random.rand(100000), "seconds")


@ureg.wraps(None, ("meter", "seconds"))
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
