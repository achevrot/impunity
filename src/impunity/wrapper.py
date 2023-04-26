from __future__ import annotations

import ast
import inspect
import os
import sys
import textwrap
import types
from pathlib import Path

# from typing_extensions import ParamSpec
from typing import Any, Callable, Optional, TypeVar, Union, overload

import astor

from .visitor import Visitor

# P = ParamSpec("P")
# T = TypeVar("T")
# T = TypeVar("T", bound=Callable[..., Any])
# OriginalFunc = Callable[P, T]  # erreur, mais pourquoi ???
# OriginalFunc = Callable[..., T]  # renvoie un OriginalFunc signature

F = TypeVar("F", bound=Callable[..., Any])  # fonctionne sur un appel direct


@overload
def impunity(__func: F) -> F:
    ...


@overload
def impunity(
    __func: None = None,
    *,
    ignore: bool = False,
    rewrite: Union[bool, str] = True,
) -> Callable[[F], F]:
    ...


def impunity(
    __func: Optional[F] = None,
    *,
    ignore: bool = False,
    rewrite: Union[bool, str] = True,
) -> Union[F, Callable[[F], F]]:
    """Decorator function to check units based on annotations

    Args:
        fun (function): decorated function

    Returns:
        new_fun (function): new function based on input
        function with eventually modified
        code to keep unit coherence.
    """

    def deco_f(fun: Callable[..., Any]):
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
        if f_str[0] == "@":
            exec(f_str[idx:])
        else:
            # if impunity is called without the decorator synthax
            exec(f_str)

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
                        co_consts = (*co_consts, const)
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
            for const in fun.__code__.co_consts:
                if const not in co_consts:
                    co_consts = (*co_consts, const)

            if sys.version_info >= (3, 11):
                fun.__code__ = types.CodeType(
                    fun.__code__.co_argcount,
                    fun.__code__.co_posonlyargcount,
                    fun.__code__.co_kwonlyargcount,
                    fun.__code__.co_nlocals,
                    fun.__code__.co_stacksize,
                    fun.__code__.co_flags,
                    new_fun.__code__.co_code,
                    co_consts,
                    fun.__code__.co_names,
                    fun.__code__.co_varnames,
                    fun.__code__.co_filename,
                    fun.__code__.co_name,
                    fun.__code__.co_qualname,
                    fun.__code__.co_firstlineno,
                    new_fun.__code__.co_linetable,
                    fun.__code__.co_exceptiontable,
                    fun.__code__.co_freevars,
                    fun.__code__.co_cellvars,
                )
            else:
                fun.__code__ = types.CodeType(
                    fun.__code__.co_argcount,
                    fun.__code__.co_posonlyargcount,
                    fun.__code__.co_kwonlyargcount,
                    fun.__code__.co_nlocals,
                    fun.__code__.co_stacksize,
                    fun.__code__.co_flags,
                    new_fun.__code__.co_code,
                    co_consts,
                    fun.__code__.co_names,
                    fun.__code__.co_varnames,
                    fun.__code__.co_filename,
                    fun.__code__.co_name,
                    fun.__code__.co_firstlineno,
                    new_fun.__code__.co_lnotab,
                    fun.__code__.co_freevars,
                    fun.__code__.co_cellvars,
                )
        return fun

    if __func is not None:
        return deco_f(__func)
    else:
        return deco_f
