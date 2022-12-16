import ast
from typing import Optional


class QuantityNode:
    def __init__(self, node: ast.AST, unit: Optional[str] = None) -> None:
        self.node = node
        self.unit = unit
