import ast
from typing import Optional, TypeVar, overload
from _collections_abc import Sequence

Unit = Optional[str]
N = TypeVar("N", bound=Optional[ast.expr], covariant=True)


class QuantityNode:
    @overload
    def __init__(self, node: N, unit: Optional[Unit] = None) -> None:
        ...

    @overload
    def __init__(self, node: N, unit: Optional[Sequence[Unit]] = None) -> None:
        ...

    def __init__(self, node, unit=None) -> None:
        self.node = node
        self.unit = unit
