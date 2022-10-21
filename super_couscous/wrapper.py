from __future__ import annotations

from functools import wraps
import inspect
import logging
import ast
from typing import Any, Callable

import pint
import astor

ReturnQuantity = Callable[..., pint.Quantity[Any]]
m = int

_log = logging.getLogger(__name__)
f_handler = logging.FileHandler("file.log")
_log.addHandler(f_handler)


class Visitor(ast.NodeTransformer):
    def visit_AnnAssign(self, node):

        new_val = ast.Constant(node.value.value * 2)
        newnode = ast.AnnAssign(
            node.target,
            annotation=node.annotation,
            value=new_val,
            simple=node.simple,
        )
        ast.copy_location(newnode, node)
        ast.fix_missing_locations(newnode)
        return newnode


def check_units(fun):
    fun_tree = ast.parse(inspect.getsource(fun))  # get the function AST
    fun_tree = Visitor().visit(fun_tree)  # send it to the NodeTransformer
    f_str = astor.to_source(
        fun_tree
    )  # get the string of the transformed function
    print(f_str)
    exec(f_str[f_str.find("\n") + 1 :])  # strip wrapper to avoid recursion
    _log.warning(f_str)
    # get from locals the new function and return it
    return locals()[fun.__name__]


# %%
