from __future__ import annotations

import ast
import inspect
import logging
import sys
import types
import typing
from math import isclose
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Optional,
    Union,
    cast,
    overload,
)

import pint
from pint import UnitRegistry
from typing_extensions import Annotated, Protocol, TypedDict, TypeGuard

from .quantityNode import QuantityNode, Unit

# annotation_node = Union[ast.Subscript, ast.Name, ast.Constant]


class HasMetadata(Protocol):
    __metadata__: tuple[str, ...]


def is_annotated(hint: Any) -> TypeGuard[HasMetadata]:
    """Determines whether the annotation is of type Annotated"""
    return isinstance(hint, type(Annotated[int, "spam"]))


_log = logging.getLogger(__name__)


class VarDict(Dict[str, Any]):
    def __missing__(self, key: str) -> None:
        msg = f"Variable {key} is not annotated. Fallback to dimensionless"
        _log.info(msg)
        return None


class PrefixSuffix(TypedDict):
    prefix: str
    suffix: str


def split_attribute(node: ast.Attribute) -> PrefixSuffix:
    """Transform the AST of a.b.c in {'prefix': 'a.b', 'suffix': 'c'}."""

    assert isinstance(node, ast.Attribute)
    suffix = node.attr
    attr = node.value
    prefix = ""
    while isinstance(attr, ast.Attribute):
        prefix = "." + attr.attr + prefix
        attr = attr.value
    if isinstance(attr, ast.Name):
        prefix = attr.id + prefix

    return dict(prefix=prefix, suffix=suffix)


class Visitor(ast.NodeTransformer):

    """Impunity AST visitor class checking for Annotations
    to transform the code if necessary

    Attributes:
        impunity_func : dict[tuple[str, str], Callable]
            Dictionnary of Callables to keep track of functions
            tracked by impunity
        ureg : pint.UnitRegistry
            Unit Registry from Pint to manage UoMs.
    """

    # tuple[module_name, function_name]
    impunity_func: ClassVar[dict[tuple[str, str], Callable[..., Any]]] = {}
    impunity_funcdef: ClassVar[dict[str, ast.FunctionDef]] = {}
    ureg = UnitRegistry()
    current_module: str = ""

    def __init__(self, fun: Callable[..., Any]) -> None:
        """
        Constructs all the necessary attributes for the visitor using the
        attributes of the fun Callable.

        Parameters
        ----------
            fun : Callable[..., Any]
                Callable checked by impunity
        """

        self.nested_flag = False
        x: Dict[str, str] = {}
        self.vars = VarDict(x)
        Visitor.current_module = fun.__module__

        # For class decorators
        if isinstance(fun, type):
            method_list = [
                getattr(fun, func)
                for func in dir(fun)
                if callable(getattr(fun, func)) and not func.startswith("__")
            ]
            if (
                init := fun.__init__  # type: ignore
            ).__class__.__name__ != "wrapper_descriptor":
                # meaning: does the class have a __init__
                # (otherwise, it's an empty slot)
                self.add_func(init)
            for function in method_list:
                self.add_func(function)
            self.class_attr: Dict[str, Unit] = {}
        else:
            self.add_func(fun)

    def fun_header(self, node: ast.AST) -> str:
        lineno = getattr(node, "lineno", 0)
        # coloffset = getattr(node, "coloffset", 0)
        firstlineno = getattr(self.fun.__code__, "co_firstlineno", 0)
        filename = getattr(self.fun.__code__, "co_filename")
        return f"{filename}::{self.fun.__name__}:{firstlineno + lineno - 1} "

    def get_annotation_unit(self, node: ast.expr) -> Optional[str]:
        """
        Return a UoM from an AST Node.
        Return None if the node is not compatible.

        :param node: Node with an annotation
        :type node: ast.expr with annotation
        :return: Optional str of the UoM
        :rtype: Optional[str]
        """

        unit = None

        if isinstance(node, ast.Constant):
            unit = node.value

        elif isinstance(node, ast.Attribute):
            res = split_attribute(node)
            module = self.fun_globals.get(res["prefix"], None)
            if module is not None:
                handle = getattr(module, res["suffix"], None)
                if is_annotated(handle):
                    unit = handle.__metadata__[0]
                if isinstance(handle, str):
                    unit = handle

        elif isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Index):
                if isinstance(node.slice.value, ast.Tuple):
                    unit_node = node.slice.value.elts[1]
            elif isinstance(node.slice, ast.Tuple):
                unit_node = node.slice.elts[1]
            if isinstance(unit_node, ast.Constant):
                unit = unit_node.value

        return unit

    def visit(self, root: ast.AST) -> ast.AST:
        """
        Initiate the visit of the root AST. Returns a checked ast.AST
        eventually modified to keep UoM coherence.

        Args:
            root : ast.AST
                root of the AST to visit
        """

        # Adding the "parent" attribute to every nodes of the AST
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                child.parent = node  # type: ignore
        method = "visit_" + root.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        new_node = visitor(root)
        return new_node

    @classmethod
    def add_func(cls, fun: Callable[..., Any] | ast.FunctionDef) -> None:
        """Add function to the impunity function dictionnary"""
        if isinstance(fun, ast.FunctionDef):
            cls.impunity_funcdef[fun.name] = fun
        else:
            cls.impunity_func[fun.__module__, fun.__name__] = fun

    @overload
    def get_func(self, name: str, module: None) -> None | ast.FunctionDef:
        ...

    @overload
    def get_func(self, name: str, module: str) -> None | Callable[..., Any]:
        ...

    def get_func(
        self, name: str, module: None | str = None
    ) -> None | ast.FunctionDef | Callable[..., Any]:
        result: None | ast.FunctionDef | Callable[..., Any] = None

        if module is None:
            # Check if nested function
            result = self.impunity_funcdef.get(name, None)
            if result is None:
                # If not nested, check if in globals
                fun = self.fun_globals.get(name, None)
                if fun is not None:
                    # if in globals, check if impunified
                    result = self.impunity_func.get(
                        (fun.__module__, name), None
                    )
            return result

        result = self.impunity_func.get((module, name), None)
        if result is None:
            m = self.fun_globals.get(module, None)
            if m is not None:
                result = self.impunity_func.get((m.__name__, name), None)
        return result

    def node_convert(
        self,
        expected_unit: Optional[str],
        received_unit: Optional[str],
        received_node: ast.expr,
    ) -> ast.expr:
        """check if the expected and the received units are coherents with
        each other by using the Pint library. Modify the received node
        accordingly and returns it.

        Parameters:
            - expected_unit : str
                expected Unit of Measure string
            - received_unit : str
                received Unit of Measure string
            - received_node : QuantityNode
                received Quantity Node

        Returns:
            - QuantityNode: Input Quantity Node, eventually modified for unit
            coherence.

        """
        if (
            received_unit != expected_unit
            and "dimensionless"
            not in (
                received_unit,
                expected_unit,
            )
            and received_unit is not None
        ):
            received_pint_unit = pint.Unit(received_unit)  # type: ignore
            expected_pint_unit = pint.Unit(expected_unit)  # type: ignore
            if received_pint_unit.is_compatible_with(expected_pint_unit):
                Q_ = self.ureg.Quantity
                r0 = Q_(0, received_unit)  # type: ignore
                r1 = Q_(1, received_unit)  # type: ignore
                r10 = Q_(10, received_unit)  # type: ignore

                e0 = r0.to(expected_unit)
                e1 = r1.to(expected_unit)
                e10 = r10.to(expected_unit)

                if r0.m == e0.m:
                    conv_value = expected_pint_unit.from_(received_pint_unit).m

                    if conv_value == 1:
                        new_node = received_node
                    else:
                        new_node = ast.BinOp(
                            received_node,
                            ast.Mult(),
                            ast.Constant(conv_value),
                        )

                elif (e1.m - e0.m) == 1:
                    conv_value = (
                        expected_pint_unit.from_(received_pint_unit).m
                    ) - 1

                    # if conv_value == 0:
                    #     new_node = received_node
                    # else:
                    new_node = ast.BinOp(
                        received_node,
                        ast.Add(),
                        ast.Constant(conv_value),
                    )

                elif isclose(10 * (e1.m - e0.m) + e0.m, e10.m):
                    new_node = ast.BinOp(
                        ast.BinOp(
                            received_node,
                            ast.Mult(),
                            ast.Constant((e1.m - e0.m)),
                        ),
                        ast.Add(),
                        ast.Constant(e0.m),
                    )
                else:
                    new_node = received_node  # log

            else:
                _log.warning(
                    self.fun_header(received_node)
                    + f"Expected unit {expected_unit} "
                    + f"but received incompatible unit {received_unit}."
                )
                new_node = received_node
        else:
            new_node = received_node
        return new_node

    def get_annotations(
        self, name: str, module: None | str = None
    ) -> Optional[Dict[str, Any]]:
        """Get annotations of a function found in the impunity_func class dict.
        Returns None if the function is not annotated.

        Parameters:
            - name : str
                name of the function for which annotations are required

        Returns:
            - Optional dict of annotations
        """

        if (fun := self.get_func(name, module)) is not None:
            if annotations := getattr(fun, "__annotations__", None):
                globals = list(self.impunity_func.values())[-1].__globals__
                locals = fun.__globals__  # type: ignore
                annotations = {
                    k: v
                    if not isinstance(v, str)
                    else eval(v, globals, locals)
                    for k, v in annotations.items()
                }
                return cast(Dict[str, Any], annotations)
        elif callable(name):
            if annotations := getattr(name, "__annotations__", None):
                globals = list(self.impunity_func.values())[-1].__globals__
                locals = name.__globals__  # type: ignore
                annotations = {
                    k: v
                    if not isinstance(v, str)
                    else eval(v, globals, locals)
                    for k, v in annotations.items()
                }
                return cast(Dict[str, Any], annotations)

        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Method called by the visitor if the visited node is
        function defintion. Is usually the root node in impunity

        Args:
            node (ast.FunctionDef): Visited Function Definition

        """
        # if not self.nested_flag:  # TODO
        #     self.func_flush()
        # check for impunity decorator:
        if node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and isinstance(
                    decorator.func, ast.Name
                ):
                    if decorator.func.id == "impunity":
                        for kw in decorator.keywords:
                            if hasattr(kw, "value"):
                                if (
                                    kw.arg == "ignore"
                                    and kw.value.value  # type: ignore
                                ):
                                    self.impunity_func.pop(
                                        (self.current_module, node.name), False
                                    )
                                    return node

        if (fun := self.get_func(node.name, self.current_module)) is not None:
            self.nested_flag = True
            self.fun = fun
            self.fun_globals = fun.__globals__
            if getattr(self, "class_attr", False):
                self.vars.update(self.class_attr)
        elif self.nested_flag:
            self.add_func(node)
        else:
            return node

        # Adding all annotations from own module
        annotations = getattr(
            sys.modules[self.fun.__module__], "__annotations__", None
        )
        if annotations is not None:
            for name, anno in annotations.items():
                if is_annotated(anno):
                    self.vars[name] = anno.__metadata__[0]
                if isinstance(anno, str):
                    self.vars[name] = anno

        # Adding all annotations from imported modules
        for _, val in self.fun_globals.items():
            if isinstance(val, types.ModuleType):
                annotations = getattr(val, "__annotations__", {})
                for name, anno in annotations.items():
                    if is_annotated(anno):
                        x = anno.__metadata__[0]
                        self.vars[name] = x
                    if isinstance(anno, str):
                        self.vars[name] = anno

        # from function signature
        for arg in node.args.args:
            if arg.annotation is not None:
                anno_unit = self.get_annotation_unit(arg.annotation)
                if anno_unit is not None and anno_unit in self.ureg:
                    self.vars[arg.arg] = anno_unit
                else:
                    self.vars[arg.arg] = None
                    # Removing this warning: not all parameters have to be
                    # physical quantities
                    # _log.warning(
                    #     self.fun_header(node)
                    #     + "Signature of annotated functions must be "
                    #     + "of type string or typing.Annotated"
                    # )

        # Check units in the return node
        node = cast(ast.FunctionDef, self.generic_visit(node))
        return node

    def get_node_unit(self, node: Optional[ast.expr]) -> QuantityNode:
        """Method to induce the unit of a node through recursive
        calls on children if any.

        Args:
            node (ast.AST): input node

        Returns:
            QuantityNode: QuantityNode(node, induced_unit)
        """

        new_node: Union[ast.BinOp, ast.IfExp, ast.Call]

        if isinstance(node, ast.Constant):
            return QuantityNode(node, None)  # self.vars[node.value])
        if isinstance(node, ast.Attribute):
            return QuantityNode(node, self.vars[node.attr])
        if isinstance(node, ast.Subscript):
            return QuantityNode(node, self.get_node_unit(node.value).unit)
        elif isinstance(node, ast.Tuple):
            elems = list(map(self.get_node_unit, node.elts))
            if len(elems) == 1:
                return QuantityNode(elems[0].node, elems[0].unit)
            else:
                # TODO Sequence[Unit] should we clean?
                return QuantityNode(
                    ast.Tuple([elem.node for elem in elems], ctx=node.ctx),
                    [elem.unit for elem in elems],  # type: ignore
                )
        elif isinstance(node, ast.List):
            _log.warning(
                self.fun_header(node)
                + "lists are not supported by impunity (but numpy arrays are)"
            )
            return QuantityNode(node, "dimensionless")

        elif isinstance(node, ast.Set):
            # TODO Sequence[Unit] should we clean?
            elems = list(map(self.get_node_unit, node.elts))
            return QuantityNode(
                ast.Set([elem.node for elem in elems]),
                [elem.unit for elem in elems],  # type: ignore
            )

        elif isinstance(node, ast.Dict):
            if not node.keys:
                return QuantityNode(node, None)
            else:
                # TODO Sequence[Unit] should we clean?
                elems = list(map(self.get_node_unit, node.values))
                return QuantityNode(
                    ast.Dict(zip(node.keys, [elem.node for elem in elems])),
                    [elem.unit for elem in elems],  # type: ignore
                )
        elif isinstance(node, ast.Name):
            return QuantityNode(node, self.vars[node.id])

        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub)
        ):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            if left.unit is None or right.unit is None:
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(
                    ast.copy_location(new_node, node),
                    left.unit if left.unit is not None else right.unit,
                )

            if pint.Unit(left.unit).is_compatible_with(  # type: ignore
                pint.Unit(right.unit)  # type: ignore
            ):
                conv_value = (
                    pint.Unit(left.unit)  # type: ignore
                    .from_(pint.Unit(right.unit))  # type: ignore
                    .m
                )
                new_node = ast.BinOp(
                    left.node,
                    node.op,
                    ast.BinOp(
                        right.node, ast.Mult(), ast.Constant(conv_value)
                    ),
                )
                return QuantityNode(
                    ast.copy_location(new_node, node), left.unit
                )

            else:
                _log.warning(
                    self.fun_header(node)
                    + f"Type {left.unit} and {right.unit} "
                    + "are not compatible. Fallback to dimensionless"
                )
                return QuantityNode(node, "dimensionless")

        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Mult, ast.Div)
        ):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            if left.unit is None or right.unit is None:
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(
                    ast.copy_location(new_node, node),
                    left.unit if left.unit is not None else right.unit,
                )

            if is_annotated(left.unit):
                left.unit = left.unit.__metadata__[0]

            if is_annotated(right.unit):
                right.unit = right.unit.__metadata__[0]

            if pint.Unit(left.unit).is_compatible_with(  # type: ignore
                pint.Unit(right.unit)  # type: ignore
            ):
                conv_value = (
                    pint.Unit(left.unit)  # type: ignore
                    .from_(pint.Unit(right.unit))  # type: ignore
                    .m
                )
                new_node = ast.BinOp(
                    left.node,
                    node.op,
                    ast.BinOp(
                        right.node, ast.Mult(), ast.Constant(conv_value)
                    ),
                )
                unit = (
                    f"{left.unit}*{left.unit}"
                    if isinstance(node.op, ast.Mult)
                    else "dimensionless"
                )
                return QuantityNode(ast.copy_location(new_node, node), unit)

            else:
                new_node = ast.BinOp(left.node, node.op, right.node)
                unit = (
                    f"{left.unit}*{right.unit}"
                    if isinstance(node.op, ast.Mult)
                    else f"{left.unit}/{right.unit}"
                )
                return QuantityNode(ast.copy_location(new_node, node), unit)

        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            if left.unit is None:
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(
                    ast.copy_location(new_node, node),
                    left.unit if left.unit is not None else None,
                )

            if is_annotated(left.unit):
                left.unit = left.unit.__metadata__[0]

            if is_annotated(right.unit):
                right.unit = right.unit.__metadata__[0]

            if left.unit == "dimensionless":
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(new_node, "dimensionless")

            if right.unit is not None:
                _log.warning(
                    self.fun_header(node)
                    + "The exponent cannot be evaluated statically or is "
                    + "not dimensionless."
                )

                return QuantityNode(node, None)

            elif isinstance(right.node, ast.Constant):
                unit = f"({left.unit})^({right.node.value})"
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(new_node, unit)

            elif isinstance(right.node, ast.BinOp):
                pow_right = right.node.right
                pow_left = right.node.left
                if isinstance(pow_left, ast.Constant) and isinstance(
                    pow_right, ast.Constant
                ):
                    if isinstance(right.node.op, ast.Mult):
                        unit = (
                            f"({left.unit})^({pow_left.value}"
                            + f"*{pow_right.value})"
                        )
                    elif isinstance(right.node.op, ast.Div):
                        unit = (
                            f"({left.unit})^({pow_left.value}"
                            + f"/{pow_right.value})"
                        )
                    elif isinstance(right.node.op, ast.Add):
                        unit = (
                            f"({left.unit})^({pow_left.value}"
                            + f"+{pow_right.value})"
                        )
                    elif isinstance(right.node.op, ast.Sub):
                        unit = (
                            f"({left.unit})^({pow_left.value}"
                            + f"-{pow_right.value})"
                        )
                    else:
                        _log.warning(
                            self.fun_header(node)
                            + "The exponent cannot be statically evaluated or "
                            + "is not dimensionless."
                        )
                        new_node = ast.BinOp(left.node, node.op, right.node)
                        return QuantityNode(new_node, None)
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(new_node, unit)

            else:
                _log.warning(
                    self.fun_header(node)
                    + "The exponent cannot be statically evaluated or "
                    + "is not dimensionless."
                )
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(new_node, None)

        elif isinstance(node, ast.BinOp):
            _log.warning(
                self.fun_header(node) + "Binary Operation not supported yet."
            )
            return QuantityNode(node, None)

        elif isinstance(node, ast.IfExp):
            body = self.get_node_unit(node.body)
            orelse = self.get_node_unit(node.orelse)

            new_node = ast.IfExp(
                test=node.test, body=body.node, orelse=orelse.node
            )

            if body.unit != orelse.unit:
                _log.warning(
                    self.fun_header(node)
                    + "Ternary operator with mixed units."
                )
                return QuantityNode(ast.copy_location(new_node, node), None)
            else:
                return QuantityNode(
                    ast.copy_location(new_node, node), body.unit
                )

        elif isinstance(node, ast.Call):
            node = self.generic_visit(node)  # type: ignore
            if isinstance(node.func, ast.Name):
                id_ = node.func.id
                module = None
            elif isinstance(node.func, ast.Attribute):
                res = split_attribute(node.func)
                id_ = res["suffix"]
                module = res["prefix"]

            signature = self.get_annotations(id_, module)

            new_args = []
            offset = 0

            # if not a known impunity function or no return signature
            if (
                signature is None
                or not signature
                or list(signature.items())[-1][0] != "return"
            ):
                return QuantityNode(node, None)
            else:
                fun_signature = list(signature.items())[:-1]
                return_signature = list(signature.items())[-1]

                for i, arg in enumerate(node.args):
                    expected = fun_signature[i + offset][1]
                    if fun_signature[i][0] == "self":
                        offset = 1
                    if is_annotated(expected):
                        expected = expected.__metadata__[0]

                    msg = (
                        self.fun_header(node)
                        + f"Function {id_} expected unit "
                        + f"{expected} but received unitless quantity"
                    )

                    if (received := self.get_node_unit(arg)).unit is None:
                        if expected is not inspect._empty:
                            _log.warning(msg)
                        new_args.append(arg)
                        continue

                    received.unit = (
                        received.unit.__metadata__[0]
                        if is_annotated(received.unit)
                        else received.unit
                    )

                    assert received.node is not None
                    new_arg = self.node_convert(
                        expected, received.unit, received.node
                    )
                    new_args.append(new_arg)

            new_node = (
                node
                if not new_args
                else ast.Call(
                    func=node.func,
                    args=new_args,
                    keywords=node.keywords,
                )
            )

            return_unit = (
                return_signature[1].__metadata__[0]
                if is_annotated(return_signature[1])
                else return_signature[1]
            )

            return QuantityNode(ast.copy_location(new_node, node), return_unit)

        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if node.value.id == "self":
                    return QuantityNode(node, self.class_attr[node.attr])
            return QuantityNode(node, None)

        else:
            return QuantityNode(node, None)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Method called by the visitor if the visited node is a Call node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.Call): input node

        """

        if isinstance(node.func, ast.Name):
            fun_id = node.func.id
        elif isinstance(node.func, ast.Attribute):
            res = split_attribute(node.func)
            fun_id = res["prefix"] + "." + res["suffix"]

        if fun_id in __builtins__.keys():  # type: ignore
            node = self.generic_visit(node)  # type: ignore
            return node

        # parameters = inspect.getfullargspec(self.fun_globals[
        # node.func.id])
        signature = self.get_annotations(fun_id)

        new_args: list[ast.BinOp | ast.expr] = []
        new_keywords: list[ast.BinOp | ast.expr] = []
        if node.args or node.keywords:
            if signature:
                fun_signature = list(signature.items())[:-1]
            else:
                return node
            for i, arg in enumerate(node.args):
                if (received := self.get_node_unit(arg)).unit != (
                    expected := fun_signature[i][1]
                ):
                    if is_annotated(expected):
                        expected = expected.__metadata__[0]
                    assert received.node is not None
                    new_arg = self.node_convert(
                        expected, received.unit, received.node
                    )
                    new_args.append(new_arg)
                else:
                    new_args.append(arg)

            for keyword in node.keywords:
                if keyword.arg:
                    if (received := self.get_node_unit(keyword.value)) != (
                        expected := signature[keyword.arg]
                    ):
                        if is_annotated(expected):
                            x = expected.__metadata__[0]
                            expected = x
                        if not (
                            isinstance(expected, str)
                            and isinstance(received.unit, str)
                        ):
                            # TODO To avoid annoying typing for now
                            return node

                        assert received.node is not None
                        new_value = self.node_convert(
                            expected, received.unit, received.node
                        )

                        new_keyword = cast(
                            ast.expr,
                            ast.keyword(
                                keyword.arg,
                                new_value,
                            ),
                        )

                        new_keywords.append(new_keyword)

        if new_args or new_keywords:
            new_node = ast.Call(
                func=node.func,
                args=new_args,
                keywords=new_keywords,
            )

            return ast.copy_location(new_node, node)

        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AnnAssign:
        """Method called by the visitor if the visited node is an
        Annotated Assignement node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.AnnAssign): input node

        """

        value = self.get_node_unit(node.value)

        if value.node is None:
            expected_unit = self.get_annotation_unit(node.annotation)
            self.vars[node.target.id] = expected_unit  # type: ignore
            return node

        if value.node != node.value:
            new_node = ast.AnnAssign(
                target=node.target,
                annotation=node.annotation,
                value=value.node,
                simple=node.simple,
            )

            node = ast.copy_location(new_node, node)

        if value.unit is None:
            new_node = node

        else:
            expected_unit = self.get_annotation_unit(node.annotation)
            if is_annotated(value.unit):
                value.unit = value.unit.__metadata__[0]

            assert value.node is not None
            new_value = self.node_convert(
                expected_unit, value.unit, value.node
            )
            new_node = ast.AnnAssign(
                target=node.target,
                annotation=node.annotation,
                value=new_value,
                simple=node.simple,
            )

        if isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name):
                if node.target.value.id == "self":
                    self.class_attr[node.target.attr] = value.unit
        else:
            if isinstance(node.target, ast.Name):
                annotation = self.get_annotation_unit(node.annotation)
                self.vars[node.target.id] = annotation

        return ast.copy_location(new_node, node)

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        """Method called by the visitor if the visited node is an
        Binary Operation node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.BinOp): input node

        """

        return self.get_node_unit(node).node  # type: ignore

    def visit_For(self, node: ast.For) -> ast.For:
        """Method called by the visitor if the visited node is a for loop node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.For): input node

        """
        if isinstance(node.target, ast.Name):
            self.vars[node.target.id] = None
        self.generic_visit(node)
        return node

    def visit_ListComp(self, node: ast.ListComp) -> ast.ListComp:
        """Method called by the visitor if the visited node is a List
        Comprehension node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.ListComp): input node

        """

        # Calling the comprehension before the generic
        # visit to get indices into self.vars
        self.visit_comprehension(node.generators[0])
        self.generic_visit(node)
        return node

    def visit_comprehension(
        self, node: ast.comprehension
    ) -> ast.comprehension:
        """Method called by the visitor if the visited node is a
        Comprehension node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.comprehension): input node

        """

        if isinstance(node.target, ast.Name):
            self.vars[node.target.id] = None
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Method called by the visitor if the visited node is an
        Assignement node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.Assign): input node

        """
        value = self.get_node_unit(node.value)

        if value.unit is None:
            return node
        if value.node != node.value:
            new_node = ast.Assign(
                targets=node.targets,
                value=value.node,
            )
            node = ast.copy_location(new_node, node)

        new_node = ast.Assign(
            targets=node.targets,
            value=value.node,
            type_comment=f"unit: {value.unit}",
        )

        for target in node.targets:
            if isinstance(target, ast.Tuple):
                received = (
                    [
                        arg.__metadata__[0] if is_annotated(arg) else arg
                        for arg in value.unit.__args__
                    ]
                    if hasattr(value.unit, "__args__")
                    else value.unit
                )
                for i, elem in enumerate(target.elts):
                    if isinstance(elem, ast.Name):
                        if isinstance(received[i], typing.ForwardRef):
                            self.vars[elem.id] = received[i].__forward_arg__
                        else:
                            self.vars[elem.id] = received[i]

            elif isinstance(target, ast.Name):
                if target.id in self.vars:
                    expected = self.vars[target.id]
                    assert value.node is not None
                    new_value = self.node_convert(
                        expected, value.unit, value.node
                    )
                    new_node = ast.Assign(
                        targets=node.targets,
                        value=new_value,
                    )
                else:
                    self.vars[target.id] = value.unit
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        self.class_attr[target.attr] = value.unit

        return ast.copy_location(new_node, node)

    def visit_Return(self, node: ast.Return) -> ast.Return:
        """Method called by the visitor if the visited node is a
        Return node.
        Checks the units in the node and returns it eventually modified.

        Args:
            node (ast.Return): input node

        """

        for frameinfo in inspect.stack():
            if frameinfo.function == "visit_FunctionDef":
                fun = frameinfo.frame.f_locals["node"].name
                break

        return_annotation = self.get_annotations(fun, self.current_module)
        received = self.get_node_unit(node.value)

        if received.node != node.value:
            new_node = ast.Return(value=received.node)
            node = ast.copy_location(new_node, node)

        if isinstance(return_annotation, dict):
            ret = return_annotation.get("return", None)
            if ret is None:
                _log.info(
                    self.fun_header(node)
                    + "Some return annotations are missing"
                )
                new_node = node
                return ast.copy_location(new_node, node)

            if is_annotated(ret):
                # if len(ret.__args__) > 1:
                #    expected = [
                #        x.__metadata__[0] if is_annotated(x) else x
                #        for x in ret.__args__
                #    ]
                # else:
                expected = ret.__metadata__[0]
            elif not isinstance(expected := ret, str):
                # if string annotations, keep going, otherwise stop
                new_node = node
                return ast.copy_location(new_node, node)
        else:  # is None
            _log.info(
                self.fun_header(node) + "Some return annotations are missing"
            )
            new_node = node
            return ast.copy_location(new_node, node)

        if is_annotated(received.unit):
            received.unit = received.unit.__metadata__[0]

        if isinstance(expected, list):
            if isinstance(received.unit, list):
                new_node = node
            else:
                _log.warning(
                    self.fun_header(node)
                    + "Expected more than one return value"
                )
                new_node = node
        else:
            if isinstance(received.unit, list):
                _log.warning(
                    self.fun_header(node)
                    + "Expected more than one return value"
                )
                new_node = node
            else:
                assert received.node is not None
                new_value = self.node_convert(
                    expected, received.unit, received.node
                )
                new_node = ast.Return(value=new_value)

        return ast.copy_location(new_node, node)
