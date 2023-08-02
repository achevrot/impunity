from typing import Any

from impunity import impunity
from typing_extensions import Annotated


@impunity
def speed_to_test(
    d: Annotated[Any, "m"], t: Annotated[Any, "s"]
) -> Annotated[Any, "m/s"]:
    return d / t


@impunity
def speed_altitude_to_test(
    d: Annotated[Any, "m"], t: Annotated[Any, "s"], a: Annotated[Any, "m"] = 0
) -> Annotated[Any, "m/s"]:
    return d / t + a * 1.3654
