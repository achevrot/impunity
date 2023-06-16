from __future__ import annotations

import ast
import inspect
import logging
import sys
import types
import typing
from numbers import Number
from typing import Any, Dict, Optional, Union, cast
from math import isclose

if sys.version_info >= (3, 9):
    from _collections_abc import Callable, Sequence
else:
    from collections import Callable
    from typing import Sequence

import pint
from pint import UnitRegistry

if sys.version_info >= (3, 10):
    # TBH Annotated from 3.9, TypeGuard from 3.10
    from typing import Annotated, TypeGuard
else:
    from typing_extensions import Annotated, TypeGuard

from .quantityNode import QuantityNode, Unit

annotation_node = Union[ast.Subscript, ast.Name, ast.Constant]


# class annot_type(Annotated[int, "spam"]):
#     """Class to access __metadata__ from Annotated variables"""

#     def __init__(self, *args, **kw):
#         super(annot_type, self).__init__(*args, **kw)
#         self.__metadata__ = getattr(super(), "__metadata__")

annot_type = type(Annotated[int, "spam"])


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # Creates a file "todays_date.py" with warnings
        logging.StreamHandler(sys.stdout),
    ],
)

_log = logging.getLogger(__name__)


class VarDict(dict):
    def __missing__(self, key):
        if isinstance(key, Number):
            pass
        else:
            _log.warning(
                f"The variable {key} is not annotated. "
                + "Defaulted to dimensionless"
            )
        return None


def get_annotation_unit(
    annotation: annotation_node | ast.expr,
) -> Optional[str]:
    unit = None
    if isinstance(annotation, ast.Constant):
        unit = annotation.value
    elif isinstance(annotation, ast.Subscript):
        if isinstance(annotation.slice, ast.Index):
            if isinstance(annotation.slice.value, ast.Tuple):  # type: ignore
                unit_node = annotation.slice.value.elts[1]  # type: ignore
        elif isinstance(annotation.slice, ast.Tuple):
            unit_node = annotation.slice.elts[1]
        if isinstance(unit_node, ast.Constant):
            unit = unit_node.value

    return unit


def is_annotated(
    hint: Any, annot_type=annot_type
) -> TypeGuard[annot_type]:  # type: ignore
    return (type(hint) is annot_type) and hasattr(hint, "__metadata__")


class Visitor(ast.NodeTransformer):
    couscous_func: dict[str, Callable] = {}
    ureg = UnitRegistry()

    def visit(self, root: ast.AST) -> Any:
        # Adding the "parent" attribute to every nodes of the AST
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                child.parent = node  # type: ignore
        method = "visit_" + root.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        new_node = visitor(root)
        return new_node

    @classmethod
    def add_func(cls, fun):
        if isinstance(fun, ast.FunctionDef):
            cls.couscous_func[fun.name] = fun
        else:
            cls.couscous_func[fun.__name__] = fun

    def node_convert(self, expected_unit, received_unit, received_node):
        if (
            received_unit != expected_unit
            and "dimensionless"
            not in (
                received_unit,
                expected_unit,
            )
            and received_unit is not None
        ):
            if pint.Unit(received_unit).is_compatible_with(
                pint.Unit(expected_unit)
            ):
                Q_ = self.ureg.Quantity
                r0 = Q_(0, received_unit)
                r1 = Q_(1, received_unit)
                r10 = Q_(10, received_unit)

                e0 = r0.to(expected_unit)
                e1 = r1.to(expected_unit)
                e10 = r10.to(expected_unit)

                if r0.m == e0.m:
                    conv_value = (
                        pint.Unit(expected_unit)
                        .from_(pint.Unit(received_unit))
                        .m
                    )

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
                        pint.Unit(expected_unit)
                        .from_(pint.Unit(received_unit))
                        .m
                    ) - 1

                    if conv_value == 0:
                        new_node = received_node
                    else:
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
                    f"In function {self.fun.__module__}/"
                    + f"{self.fun.__name__}: "
                    + f"Expected unit {expected_unit} "
                    + f"but received incompatible unit {received_unit}."
                )
                new_node = received_node
        else:
            new_node = received_node
        return new_node

        # # Converting by multiplying
        # if conv_type == "mul":
        #     if isinstance(original_node, ast.List):
        #         # converted_node = ast.Expression(
        #         #     body=ast.GeneratorExp(elt=ast.BinOp(
        #         #         (left=ast.Name(id='n', ctx=Load()),
        #         #          op=ast.(), right=Num(n=conv_value)), generators=

        #         # ))))
        #         pass
        #     else:
        #         converted_node = ast.BinOp(
        #             original_node, ast.Mult(), ast.Constant(conv_value)
        #         )

        # if conv_type == "add":
        #     pass
        # if conv_type == "log":
        #     pass

        # return ast.copy_location(converted_node, original_node)

    # @classmethod
    # def insert_node_above(cls, original_node, new_node) -> None:
    #     parent_function: ast.AST = original_node.parent
    #     line_node: ast.AST = original_node
    #     while not isinstance(parent_function, ast.FunctionDef):
    #         line_node = parent_function
    #         # TODO Inherit AST NODE to get parents. Ignored as for now
    #         parent_function = parent_function.parent  # type: ignore

    #     new_body = parent_function.body.copy()
    #     for i, node in enumerate(parent_function.body):
    #         if line_node == node:
    #             new_body.insert(i, new_node)
    #     parent_function.body = new_body

    @classmethod
    def func_flush(cls):
        return

    @classmethod
    def get_annotations(cls, name) -> Optional[Dict[str, Any]]:
        # if sys.version_info >= (3, 10):
        #     from inspect import get_annotations as get_ann

        #     if callable(name):
        #         return get_ann(name, eval_str=True)
        #     else:
        #         return cls.couscous_func.get(name)
        # if isinstance(fun := cls.couscous_func.get(name), ast.FunctionDef):
        #     params = {}
        #     for arg in fun.args.args:
        #         ann = arg.annotation
        #         annotation = inspect.Parameter.empty
        #         if isinstance(ann, ast.Constant):
        #             annotation = ann.value
        #         elif isinstance(ann, ast.Name):
        #             annotation = ann.id
        #         elif isinstance(ann, ast.Subscript):
        #             data_type = eval(ann.slice.elts[0].id)
        #             annotation = ann.slice.elts[1].value
        #             annotation = Annotated[data_type, annotation]
        #         params.append(
        #             inspect.Parameter(
        #                 arg.arg,
        #                 inspect.Parameter.POSITIONAL_OR_KEYWORD,
        #                 annotation=annotation,
        #             )
        #         )
        #     return inspect.Signature(
        #         params,
        #         return_annotation=fun.returns.value
        #         if not getattr(fun, "returns", False)
        #         else inspect._empty,
        #     )
        if (fun := cls.couscous_func.get(name)) is not None:
            annotations = getattr(fun, "__annotations__", None)
            if annotations:
                # globals = list(cls.couscous_func.values())[-1].__globals__
                # locals = fun.__globals__
                # annotations = {
                #     k: v
                #     if not isinstance(v, str)
                #     else eval(v, globals, locals)
                #     for k, v in annotations.items()
                # }
                return cast(Dict, annotations)
        elif callable(name):
            annotations = getattr(name, "__annotations__", None)
            if annotations:
                # globals = list(cls.couscous_func.values())[-1].__globals__
                # locals = name.__globals__
                # annotations = {
                #     k: v
                #     if not isinstance(v, str)
                #     else eval(v, globals, locals)
                #     for k, v in annotations.items()
                # }
                return cast(Dict, annotations)

        return None

    @classmethod
    def get_func(cls, name):
        return cls.couscous_func.get(name)

    def __init__(self, fun) -> None:
        self.nested_flag = False
        x: Dict[str, str] = {}
        self.vars = VarDict(x)

        # For class decorators
        if isinstance(fun, type):
            method_list = [
                getattr(fun, func)
                for func in dir(fun)
                if callable(getattr(fun, func)) and not func.startswith("__")
            ]
            self.add_func(fun.__init__)  # type: ignore
            for function in method_list:
                self.add_func(function)
            self.class_attr: Dict[str, Unit] = {}
        else:
            self.add_func(fun)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if not self.nested_flag:
            self.func_flush()
        # check for couscous decorator:
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
                                    self.couscous_func.pop(node.name, False)
                                    return node

        if (fun := self.get_func(node.name)) is not None:
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
                    self.vars[name] = anno.__metadata__[0]  # type: ignore
                if isinstance(anno, str):
                    self.vars[name] = anno

        # Adding all annotations from imported modules
        for _, val in self.fun_globals.items():
            if isinstance(val, types.ModuleType):
                annotations = getattr(val, "__annotations__", None)
                if annotations is not None:
                    for name, anno in annotations.items():
                        if is_annotated(anno):
                            x = anno.__metadata__[0]  # type: ignore
                            self.vars[name] = x
                        if isinstance(anno, str):
                            self.vars[name] = anno

        # from function signature
        for arg in node.args.args:
            if arg.annotation is not None:
                anno_unit = get_annotation_unit(arg.annotation)
                if anno_unit is not None and anno_unit in self.ureg:
                    self.vars[arg.arg] = anno_unit
                else:
                    self.vars[arg.arg] = None
                    _log.warning(
                        f"In function {self.fun.__module__}/"
                        + f"{self.fun.__name__}: "
                        + "Signature of annotated functions must be "
                        + "of type string or typing.Annotated"
                    )

        # Check units in the return node
        node = self.generic_visit(node)  # type: ignore
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
        if isinstance(node, ast.Subscript):
            return QuantityNode(node, self.get_node_unit(node.value).unit)
        elif isinstance(node, ast.Tuple):
            elems = list(map(self.get_node_unit, node.elts))
            if len(elems) == 1:
                return QuantityNode(elems[0].node, elems[0].unit)
            else:
                return QuantityNode(
                    ast.Tuple([elem.node for elem in elems], ctx=node.ctx),
                    cast(Sequence[Unit], [elem.unit for elem in elems]),
                )
        elif isinstance(node, ast.List):
            _log.warning(
                f"In function {self.fun.__module__}"
                + f"/{self.fun.__name__}"
                + ": List not supported by impunity. "
                + "Please use numpy arrays."
            )
            return QuantityNode(node, "dimensionless")

        elif isinstance(node, ast.Set):
            elems = list(map(self.get_node_unit, node.elts))
            return QuantityNode(
                ast.Set([elem.node for elem in elems]),
                cast(Sequence[Unit], [elem.unit for elem in elems]),
            )

        elif isinstance(node, ast.Dict):
            if not node.keys:
                return QuantityNode(node, None)
            else:
                elems = list(map(self.get_node_unit, node.values))
                return QuantityNode(
                    ast.Dict(zip(node.keys, [elem.node for elem in elems])),
                    cast(Sequence[Unit], [elem.unit for elem in elems]),
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
                    f"In function {self.fun.__module__}/{self.fun.__name__}: "
                    + f"Type {left.unit} and {right.unit} "
                    + "are not compatible. Defaulted to dimensionless"
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
                left.unit = left.unit.__metadata__[0]  # type: ignore

            if is_annotated(right.unit):
                right.unit = right.unit.__metadata__[0]  # type: ignore

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

        elif isinstance(node, ast.BinOp):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            new_node = ast.BinOp(left.node, node.op, right.node)
            return QuantityNode(
                ast.copy_location(new_node, node),
                self.get_node_unit(node.left).unit,
            )

        elif isinstance(node, ast.IfExp):
            body = self.get_node_unit(node.body)
            orelse = self.get_node_unit(node.orelse)

            new_node = ast.IfExp(
                test=node.test, body=body.node, orelse=orelse.node
            )

            if body.unit != orelse.unit:
                _log.warning(
                    f"In function {self.fun.__module__}/{self.fun.__name__}: "
                    + "Ternary operator with mixed units"
                )
                return QuantityNode(ast.copy_location(new_node, node), None)
            else:
                return QuantityNode(
                    ast.copy_location(new_node, node), body.unit
                )

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                id = node.func.id
            elif isinstance(node.func, ast.Attribute):
                id = node.func.attr

            signature = self.get_annotations(id)

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
                        expected = expected.__metadata__[0]  # type: ignore

                    msg = (
                        f"In function {self.fun.__module__}"
                        + f"/{self.fun.__name__}: "
                        + f"Function {id} expected unit "
                        + f"{expected} but received unitless quantity"
                    )

                    if (received := self.get_node_unit(arg)).unit is None:
                        if expected is not inspect._empty:
                            _log.warning(msg)
                        new_args.append(arg)
                        continue

                    received.unit = (
                        received.unit.__metadata__[0]  # type: ignore
                        if is_annotated(received.unit)
                        else received.unit
                    )

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

            return QuantityNode(
                ast.copy_location(new_node, node), return_signature[1]
            )

        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if node.value.id == "self":
                    return QuantityNode(node, self.class_attr[node.attr])
            return QuantityNode(node, None)

        else:
            return QuantityNode(node, None)

    def visit_Call(self, node: ast.Call) -> Any:
        if isinstance(node.func, ast.Name):
            if node.func.id in __builtins__.keys():  # type: ignore
                node = self.generic_visit(node)  # type: ignore
                return node

            # parameters = inspect.getfullargspec(self.fun_globals[
            # node.func.id])
            signature = self.get_annotations(
                self.fun_globals[node.func.id]  # type: ignore
            )

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
                            expected = expected.__metadata__[0]  # type: ignore
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
                                x = expected.__metadata__[0]  # type: ignore
                                expected = x
                            if not (
                                isinstance(expected, str)
                                and isinstance(received.unit, str)
                            ):
                                # TODO To avoid annoying typing for now
                                return node

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

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        value = self.get_node_unit(node.value)

        if value is None:
            pass

        if value.node != node.value:
            new_node = ast.AnnAssign(
                target=node.target,
                annotation=node.annotation,
                value=value.node,
                simple=node.simple,
            )

            node = ast.copy_location(new_node, node)

        if value.unit is None:
            # _log.warning(
            #     f"In function {self.fun.__module__}/{self.fun.__name__}:
            # The unit of {node.target.id} could not be checked."
            # )
            new_node = node

        elif (received := value).unit != (
            expected := cast(annotation_node, node.annotation)
        ):
            expected_unit = get_annotation_unit(expected)
            if is_annotated(received.unit):
                received.unit = received.unit.__metadata__[0]  # type: ignore

            new_value = self.node_convert(
                expected_unit, received.unit, received.node
            )
            new_node = ast.AnnAssign(
                target=node.target,
                annotation=node.annotation,
                value=new_value,
                simple=node.simple,
            )

        #     if "dimensionless" in (received.unit, expected_unit):
        #         received = expected_unit
        #     if pint.Unit(received).is_compatible_with(
        #         pint.Unit(expected_unit)
        #     ):
        #         conv_value = (
        #             pint.Unit(expected_unit).from_(pint.Unit(received)).m
        #         )
        #         new_value = ast.BinOp(
        #             node.value,
        #             ast.Mult(),
        #             ast.Constant(conv_value),
        #         )
        #         new_node = ast.AnnAssign(
        #             target=node.target,
        #             annotation=node.annotation,
        #             value=new_value,
        #             simple=node.simple,
        #         )

        #     else:
        #         _log.warning(
        #             f"In function {self.fun.__module__}/{self.fun.__name__}:"
        #             + f"Assignement expected unit {expected_unit} "
        #             + f"but received incompatible unit {received}."
        #         )
        #         return node
        # else:
        #     new_node = node

        if isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name):
                if node.target.value.id == "self":
                    self.class_attr[node.target.attr] = value.unit
        else:
            if isinstance(node.target, ast.Name):
                annotation = get_annotation_unit(
                    cast(annotation_node, node.annotation)
                )
                self.vars[node.target.id] = annotation
        # ast.fix_missing_locations(new_node)
        return ast.copy_location(new_node, node)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        return self.get_node_unit(node).node

    def visit_For(self, node: ast.For) -> Any:
        if isinstance(node.target, ast.Name):
            self.vars[node.target.id] = None
        self.generic_visit(node)
        return node

    def visit_ListComp(self, node: ast.ListComp) -> Any:
        # Calling the comprehension before the generic
        # visit to get indices into self.vars
        self.visit_comprehension(node.generators[0])
        self.generic_visit(node)
        return node

    def visit_comprehension(self, node: ast.comprehension) -> Any:
        if isinstance(node.target, ast.Name):
            self.vars[node.target.id] = None
        return node

    def visit_Assign(self, node: ast.Assign) -> Any:
        value = self.get_node_unit(node.value)

        if value.unit is None:
            return node
        if value.node != node.value:
            new_node = ast.Assign(
                targets=node.targets,
                value=value.node,
            )
            node = ast.copy_location(new_node, node)

        # if isinstance(node.value, ast.Call):
        #     for target in node.targets:
        #         if isinstance(target, ast.Tuple):
        #             if isinstance(node.value.func, ast.Name):
        #                 func_name = node.value.func.id
        #             elif isinstance(node.value.func, ast.Attribute):
        #                 if isinstance(node.value.func.value, ast.Name):
        #                     func_name = (
        #                         self.vars[node.value.func.value.id]
        #                         if node.value.func.value.id in self.vars
        #                         else node.value.func.value.id
        #                     )
        #                 func_name += "." + node.value.func.attr
        #             for i, elem in enumerate(target.elts):
        #                 # if return values are tuples
        #                 if isinstance(elem, ast.Name):
        #                     if (sign := (
        # self.get_annotations(func_name))) is not None:
        #                         if is_annotated(sign["return"].__args__[i]):
        #                             self.vars[elem.id] = (
        # sign["return"].__args__[i].__metadata__[0])
        #                         else:
        #                             self.vars[elem.id] = (
        # sign["return"].__args__[i].__forward_value__)
        #         elif isinstance(target, ast.Name):
        #             if isinstance(node.value.func, ast.Name):
        #                 func_name = node.value.func.id
        #             elif isinstance(node.value.func, ast.Attribute):
        #                 if isinstance(node.value.func.value, ast.Name):
        #                     func_name = (
        #                         self.vars[node.value.func.value.id]
        #                         if node.value.func.value.id in self.vars
        #                         else node.value.func.value.id
        #                     )
        #                 func_name += "." + node.value.func.attr
        #             if (sign := self.get_annotations(func_name)) is not None:
        #                 if is_annotated(sign["return"].__args__[0]):
        #                     self.vars[target.id] = (
        # sign["return"].__args__[0].__metadata__[0])
        #                 else:
        #                     pass
        #         elif isinstance(target, ast.Attribute):
        #             if isinstance(target.value, ast.Name):
        #                 if target.value.id == "self":
        #                     self.class_attr[target.attr] = value.unit
        #     new_node = node

        new_node = ast.Assign(
            targets=node.targets,
            value=value.node,
            type_comment=f"unit: {value.unit}",
        )

        for target in node.targets:
            if isinstance(target, ast.Tuple):
                received = (
                    [
                        arg.__metadata__  # type: ignore
                        if is_annotated(arg)
                        else arg
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
                            self.vars[elem.id] = received[i][0]

            elif isinstance(target, ast.Name):
                self.vars[target.id] = value.unit
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        self.class_attr[target.attr] = value.unit

        return ast.copy_location(new_node, node)

    def visit_Return(self, node: ast.Return) -> Any:
        for frameinfo in inspect.stack():
            if frameinfo.function == "visit_FunctionDef":
                fun = frameinfo.frame.f_locals["node"].name
                break
        return_annotation = self.get_annotations(fun)
        received = self.get_node_unit(node.value)

        if received.node != node.value:
            new_node = ast.Return(value=received.node)
            node = ast.copy_location(new_node, node)

        if return_annotation is inspect._empty or return_annotation is None:
            _log.warning(
                f"In function {self.fun.__module__}/{self.fun.__name__}: "
                + "Some return annotations are missing"
            )
            new_node = node
            return ast.copy_location(new_node, node)

        if isinstance(return_annotation, Dict):
            if is_annotated(return_annotation["return"]):
                ret = return_annotation["return"]
                if len(ret.__args__) > 1:  # type: ignore
                    expected = [
                        x.__metadata__[0]  # type: ignore
                        if is_annotated(x)
                        else x
                        for x in ret.__args__  # type: ignore
                    ]
                else:
                    expected = ret.__metadata__[0]  # type: ignore
            else:  # string annotations
                expected = return_annotation["return"]
        else:
            _log.warning(
                f"In function {self.fun.__module__}/{self.fun.__name__}: "
                "Type of the return annotation not supported yet"
            )
            new_node = node
            return ast.copy_location(new_node, node)

        if is_annotated(received.unit):
            received.unit = received.unit.__metadata__[0]  # type: ignore

        if isinstance(expected, list):
            if isinstance(received.unit, list):
                new_node = node
            else:
                _log.warning(
                    f"In function {self.fun.__module__}/{self.fun.__name__}: "
                    "Expected more than one return value"
                )
                new_node = node
        else:
            if isinstance(received.unit, list):
                _log.warning(
                    f"In function {self.fun.__module__}/{self.fun.__name__}: "
                    "Expected more than one return value"
                )
                new_node = node
            else:
                new_value = self.node_convert(
                    expected, received.unit, received.node
                )
                new_node = ast.Return(value=new_value)

        return ast.copy_location(new_node, node)
