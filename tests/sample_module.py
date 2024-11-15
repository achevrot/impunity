from typing import Any

from typing_extensions import Annotated

import numpy as np
from impunity import impunity
import numpy as np

meters = Annotated[np.ndarray[Any], "m"]
seconds = Annotated[float, "s"]
meters_per_second = Annotated[np.ndarray[Any], "m/s"]


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
