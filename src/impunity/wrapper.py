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

    The **impunity** decorator provides additional parameters that allow for
    more flexibility and control over the unit coherence checking process.
    These parameters can be passed to the decorator to modify its behavior
    according to specific requirements.

    Args
    ------

    - **ignore** : bool

    The `ignore` parameter allows you to specify names of
    functions or methods that should be ignored during unit
    coherence checking. When a decorated class contains functions
    or methods that you want to exclude from the coherence checking
    process, you can use the `ignore` parameter to specify those
    functions or methods.

    .. code-block:: python

        from impunity import impunity

        @impunity
        class MyClass:

        def calculate_velocity(distance: "meters", time: "seconds") -> "m/s":
            return distance / time

        @impunity(ignore=True)
        def function_to_ignore():
            # This function will be ignored during unit coherence checking
            pass

    In this example, the `calculate_velocity`
    function is check thanks to the `@impunity` decorator of the class.
    On the other hand, `@impunity(ignore=True)` ensures that the
    `function_to_ignore` is excluded from unit coherence checking,
    allowing you to selectively ignore specific functions or methods.

    - **rewrite** : Union[bool, str]

    The `rewrite` parameter enables you to specify a file path where the
    rewritten functions will be saved. When this parameter is provided,
    the modified functions, with the necessary unit conversions added,
    will be written to the specified file.

    .. code-block:: python

        from impunity import impunity

        @impunity(rewrite="path/to/rewritten_functions.py")
        def calculate_velocity(distance: float, time: float) -> float:
            return distance / time

    In this example, the `calculate_velocity`
    function is decorated with `@impunity`
    and the `rewrite` parameter is set to `"path/to/rewritten_functions.py"`.
    After the coherence checking process, the modified function,
    with the necessary unit conversions added, will be saved to
    the specified file.

    These rewritten functions can be further utilized in your codebase,
    allowing you to work with coherent units seamlessly.
    """

    def deco_f(fun: F) -> F:
        if ignore:
            return fun

        # dedent for nested methods
        fun_tree = ast.parse(textwrap.dedent(inspect.getsource(fun)))

        visitor = Visitor(fun)
        if "forward" in fun.__name__:
            pass
        fun_tree = visitor.visit(fun_tree)  # type: ignore

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
        if f_str[0:9] == "@impunity":
            exec(f_str[idx:], visitor.fun_globals, locals())
        else:
            # if impunity is called without the decorator synthax
            exec(f_str, visitor.fun_globals, locals())

        new_fun = locals()[fun.__name__]

        if isinstance(new_fun, type):
            method_list = [
                getattr(new_fun, func)
                for func in dir(new_fun)
                if callable(getattr(new_fun, func))
                and not func.startswith("__")
            ]
            for new_method in method_list:
                origin_method = getattr(fun, new_method.__name__)
                co_consts = new_method.__code__.co_consts
                co_lnotab = new_method.__code__.co_lnotab
                for const in origin_method.__code__.co_consts:
                    if const not in co_consts:
                        co_consts = (*co_consts, const)

                if sys.version_info >= (3, 11):
                    origin_method.__code__ = types.CodeType(
                        origin_method.__code__.co_argcount,
                        origin_method.__code__.co_posonlyargcount,
                        origin_method.__code__.co_kwonlyargcount,
                        origin_method.__code__.co_nlocals,
                        origin_method.__code__.co_stacksize,
                        origin_method.__code__.co_flags,
                        new_method.__code__.co_code,
                        co_consts,
                        origin_method.__code__.co_names,
                        origin_method.__code__.co_varnames,
                        origin_method.__code__.co_filename,
                        origin_method.__code__.co_name,
                        origin_method.__code__.co_qualname,
                        origin_method.__code__.co_firstlineno,
                        new_method.__code__.co_linetable,
                        origin_method.__code__.co_exceptiontable,
                        origin_method.__code__.co_freevars,
                        origin_method.__code__.co_cellvars,
                    )
                else:
                    origin_method.__code__ = types.CodeType(
                        origin_method.__code__.co_argcount,
                        origin_method.__code__.co_posonlyargcount,
                        origin_method.__code__.co_kwonlyargcount,
                        origin_method.__code__.co_nlocals,
                        origin_method.__code__.co_stacksize,
                        origin_method.__code__.co_flags,
                        new_method.__code__.co_code,
                        co_consts,
                        origin_method.__code__.co_names,
                        origin_method.__code__.co_varnames,
                        origin_method.__code__.co_filename,
                        origin_method.__code__.co_name,
                        origin_method.__code__.co_firstlineno,
                        new_method.__code__.co_lnotab,
                        origin_method.__code__.co_freevars,
                        origin_method.__code__.co_cellvars,
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
                    new_fun.__code__.co_names,
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
                    new_fun.__code__.co_names,
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
