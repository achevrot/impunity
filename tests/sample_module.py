from typing import Any

from typing_extensions import Annotated

from impunity import impunity
import numpy.typing as npt


meters = Annotated[npt.ArrayLike, "m"]
seconds = Annotated[float, "s"]
meters_per_second = Annotated[npt.ArrayLike, "m/s"]


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


@impunity
def speed_with_annotated_to_test(
    distance: meters, time: seconds
) -> meters_per_second:
    return distance / time
