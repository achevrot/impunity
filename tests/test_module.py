import sys
from typing import Any

from impunity import impunity

if sys.version_info >= (3, 9):
    from typing import Annotated

else:
    from typing import Tuple as tuple

    from typing_extensions import Annotated


@impunity
def test_speed(
    d: Annotated[Any, "m"], t: Annotated[Any, "s"]
) -> Annotated[Any, "m/s"]:
    return d / t


@impunity
def test_speed_altitude(
    d: Annotated[Any, "m"], t: Annotated[Any, "s"], a: Annotated[Any, "m"] = 0
) -> Annotated[Any, "m/s"]:
    return d / t + a * 1.3654
