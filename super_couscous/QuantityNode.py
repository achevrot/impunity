import ast


class QuantityNode:
    def __init__(self, node: ast.AST, unit: str) -> None:
        self.node = node
        self.unit = unit
