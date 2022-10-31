from __future__ import annotations

import inspect
import logging
import ast
from pyclbr import Function
import sys
import textwrap
from typing import Any, Callable
import gc  # garbage collector

import pint
import astor
from pitot import Q_

ReturnQuantity = Callable[..., pint.Quantity[Any]]

_log = logging.getLogger(__name__)
f_handler = logging.FileHandler("file.log")
_log.addHandler(f_handler)


class AstRaise(ast.NodeTransformer):
    def get_node(self, except_name: str) -> ast.Raise:
        mod = ast.parse(f"raise {except_name}")
        self.generic_visit(mod)
        return self.exception

    def visit_Raise(self, node: ast.Raise):
        self.exception = node


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


class Visitor(ast.NodeTransformer):
    def __init__(self, fun_globals) -> None:
        self.fun_globals = fun_globals

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.vars = {}
        self.calls = {}
        # TODO : put

        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> Any:

        if isinstance(node.func, ast.Name):
            signature = inspect.signature(self.fun_globals[node.func.id])
            new_args = []
            for i, (_, value) in enumerate(signature.parameters.items()):
                if (received := self.vars[node.args[i].id]) != (
                    expected := value.annotation
                ):
                    print(
                        f"WARNING : unit '{received}' is different than '{expected}'"
                    )
                    try:
                        conv_value = Q_(str(received)).to(str(expected)).m
                    except pint.errors.DimensionalityError as e:
                        exception = (
                            str(get_full_class_name(e))
                            + f'("{received}", "{expected}")'
                        )
                        new_node = AstRaise().get_node(exception)
                        return new_node

                    new_arg = ast.BinOp(
                        node.args[i],
                        ast.Mult(),
                        ast.Constant(conv_value),
                    )
                    new_args.append(new_arg)

            if new_args:
                newnode = ast.Call(
                    func=node.func,
                    args=new_args,
                    keywords=node.keywords,
                )
                ast.copy_location(newnode, node)
                ast.fix_missing_locations(newnode)

                return newnode

        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        if isinstance(node.value, ast.Call):
            # TODO : Check if annotation = return annotation of func
            self.vars[node.target.id] = inspect.signature(
                self.fun_globals[node.value.func.value.id]
            ).return_annotation
        else:
            try:
                self.vars[node.target.id] = node.annotation.value
            except AttributeError:
                print("Units Annotation should be strings")

        self.generic_visit(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> Any:
        if isinstance(node.value, ast.Call):
            for target in node.targets:
                self.vars[target.id] = inspect.signature(
                    self.fun_globals[node.value.func.id]
                ).return_annotation

        self.generic_visit(node)
        return node


def has_quantity(node: ast.FunctionDef) -> bool:

    return_value = node.returns
    args = node.args

    if isinstance(node.returns, ast.Attribute):
        if node.returns.attr == "Quantity":
            return True
    elif isinstance(node.returns, ast.Subscript):
        return False

    return True


def check_units(fun: Function) -> Function:
    """Decorator function to check units based on annotations

    Args:
        fun (function): decorated function

    Returns:
        new_fun (function): new function based on input function with eventually modified
        code to keep unit coherence.
    """
    fun_tree = ast.parse(
        textwrap.dedent(inspect.getsource(fun))  # dedent for nested methods
    )  # get the function AST
    visitor = Visitor(fun.__globals__)
    fun_tree = visitor.visit(fun_tree)  # send it to the NodeTransformer
    f_str = astor.to_source(
        fun_tree
    )  # get the string of the transformed function
    _log.warning(f_str)
    exec(f_str[f_str.find("\n") + 1 :], fun.__globals__, locals())

    new_fun = locals()[fun.__name__]
    code = new_fun.__code__
    code.replace(co_filename="patate")
    new_fun.__code__ = new_fun.__code__.replace(
        co_filename=fun.__code__.co_filename,
        co_firstlineno=fun.__code__.co_firstlineno,
    )  # Big mess without it, especially on pytest
    return new_fun
