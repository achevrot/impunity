from typing import Annotated
from impunity import impunity


@impunity(ignore_warnings=True)
def a() -> None:
    x: Annotated[int, "m"] = 20
    y: Annotated[int, "K"] = x
    pass
