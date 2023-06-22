# %%


from typing import Annotated, Any
import numpy as np
import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

a: Annotated[Any, "meters"] = Q_(np.random.rand(100000), "meter")
b: Annotated[Any, "seconds"] = Q_(np.random.rand(100000), "hours")


@ureg.wraps(None, ("meter", "seconds"))
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
