from __future__ import annotations

import ast
from typing import Optional, TypeVar

Unit = Optional[str]
N = TypeVar("N", bound=ast.expr, covariant=True)


class QuantityNode:

    """Node object with a unit attribute.

    Attributes:
        node : TypeVar("N", bound=Optional[ast.expr], covariant=True)
            Any type of expression found within an ast.
        unit : Optional[str]
            Optional string representing a UoM.
    """

    def __init__(self, node: None | N, unit: None | Unit = None) -> None:
        self.node = node
        self.unit = unit
