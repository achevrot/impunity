from __future__ import annotations

import ast
import inspect
import logging
import textwrap
from typing import Any, Callable

import astor

from .visitor import Visitor

_log = logging.getLogger(__name__)


def impunity(
    *args: Callable[[Any], Any],
    ignore: bool = False,
) -> Callable[[Any], Any]:

    """Decorator function to check units based on annotations

    Args:
        fun (function): decorated function

    Returns:
        new_fun (function): new function based on input
        function with eventually modified
        code to keep unit coherence.
    """

    def deco_f(fun: Callable[[Any], Any]) -> Callable[[Any], Any]:
        if ignore:
            return fun

        fun_tree = ast.parse(
            textwrap.dedent(inspect.getsource(fun))  # dedent for nested methods
        )  # get the function AST
        visitor = Visitor(fun)
        fun_tree = visitor.visit(fun_tree)  # send it to the NodeTransformer
        f_str = astor.to_source(
            fun_tree
        )  # get the string of the transformed function
        exec(f_str[f_str.find("\n") + 1 :])

        new_fun = locals()[fun.__name__]

        if isinstance(new_fun, type):
            method_list = [
                getattr(new_fun, func)
                for func in dir(new_fun)
                if callable(getattr(new_fun, func))
                # TODO Add Init
                and not func.startswith("__")
            ]
            for new_method in method_list:
                origin_method = getattr(fun, new_method.__name__)
                co_consts = new_method.__code__.co_consts
                for const in origin_method.__code__.co_consts:
                    if const not in co_consts:
                        co_consts = co_consts + (const,)
                cocode = new_method.__code__.co_code

                origin_method.__code__ = origin_method.__code__.replace(
                    co_code=cocode,
                    co_consts=co_consts,
                )

        else:
            co_consts = new_fun.__code__.co_consts
            for const in fun.__code__.co_consts:
                if const not in co_consts:
                    co_consts = co_consts + (const,)
            cocode = new_fun.__code__.co_code

            fun.__code__ = fun.__code__.replace(
                co_code=cocode,
                co_consts=co_consts,
            )

        return fun

    if len(args) == 0:
        return deco_f

    return deco_f(args[0])
