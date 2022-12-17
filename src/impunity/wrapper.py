from __future__ import annotations

import ast
import inspect
import logging
import os
import textwrap
from pathlib import Path
from typing import Any, Callable, Union

import astor

from .visitor import Visitor

_log = logging.getLogger(__name__)


def impunity(
    *args: Callable[[Any], Any],
    ignore: bool = False,
    rewrite: Union[bool, str] = True,
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

        # dedent for nested methods
        fun_tree = ast.parse(textwrap.dedent(inspect.getsource(fun)))

        visitor = Visitor(fun)
        fun_tree = visitor.visit(fun_tree)

        # get the string of the transformed function
        f_str = astor.to_source(fun_tree)

        if not rewrite:
            return fun

        if isinstance(rewrite, str):
            path = Path(rewrite)
            if not path.is_absolute():
                origin_path = Path(
                    os.path.abspath(inspect.getfile(fun))
                ).parents[0]
                path = origin_path.joinpath(path)
            with open(path, "w") as f:
                idx = f_str.find("\n") + 1
                f.write(f_str[idx:])
                f.write("\n")

        idx = f_str.find("\n") + 1
        exec(f_str[idx:])

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
                co_lnotab = new_method.__code__.co_lnotab
                co_firstlineno = fun.__code__.co_firstlineno + 1
                for const in origin_method.__code__.co_consts:
                    if const not in co_consts:
                        co_consts = co_consts + (const,)
                cocode = new_method.__code__.co_code

                origin_method.__code__ = origin_method.__code__.replace(
                    co_code=cocode,
                    co_consts=co_consts,
                    co_lnotab=co_lnotab,
                    co_firstlineno=co_firstlineno,
                )

        else:
            co_consts = new_fun.__code__.co_consts
            co_lnotab = new_fun.__code__.co_lnotab
            co_firstlineno = fun.__code__.co_firstlineno + 1
            for const in fun.__code__.co_consts:
                if const not in co_consts:
                    co_consts = co_consts + (const,)
            cocode = new_fun.__code__.co_code

            fun.__code__ = fun.__code__.replace(
                co_code=cocode,
                co_consts=co_consts,
                # co_lnotab=co_lnotab,
                co_firstlineno=co_firstlineno,
            )

        return fun

    if len(args) == 0:
        return deco_f

    return deco_f(args[0])
