from __future__ import annotations

import ast
import collections
import inspect
import logging
import sys
import types
from typing import Any, Dict, Optional, Union, cast
from _collections_abc import Sequence

import pint
from pint import UnitRegistry

if sys.version_info >= (3, 10):
    # TBH Annotated from 3.9, TypeGuard from 3.10
    from typing import Annotated, TypeGuard
else:
    from typing_extensions import Annotated, TypeGuard

from .exception import raise_dim_error
from .quantityNode import QuantityNode, Unit

annotation_node = Union[ast.Subscript, ast.Name, ast.Constant]


class annot_type(Annotated[int, "spam"]):
    """Class to access __metadata__ from Annotated variables"""

    __metadata__ = getattr(super, "__metadata__")


_log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


def get_annotation_unit(annotation: annotation_node | ast.expr) -> str:
    unit = None
    if isinstance(annotation, ast.Constant):
        unit = annotation.value
    elif isinstance(annotation, ast.Subscript):
        if isinstance(annotation.slice, ast.Index):
            if isinstance(annotation.slice.value, ast.Tuple):
                unit_node = annotation.slice.value.elts[1]
        elif isinstance(annotation.slice, ast.Tuple):
            unit_node = annotation.slice.elts[1]
        if isinstance(unit_node, ast.Constant):
            unit = unit_node.value

    if unit is not None:
        return unit
    else:
        raise TypeError(f"{annotation} is not an annotation type expected by impunity")


def is_annotated(hint: Any, annot_type=annot_type) -> TypeGuard[annot_type]:  # type: ignore
    return (type(hint) is annot_type) and hasattr(hint, "__metadata__")


class Visitor(ast.NodeTransformer):
    couscous_func: dict[str, collections.Callable] = {}
    ureg = UnitRegistry()

    @classmethod
    def add_func(cls, fun):
        if isinstance(fun, ast.FunctionDef):
            cls.couscous_func[fun.name] = fun
        else:
            cls.couscous_func[fun.__name__] = fun

    @classmethod
    def func_flush(cls):
        return

    @classmethod
    def get_func_signature(cls, name):
        if isinstance(fun := cls.couscous_func.get(name), ast.FunctionDef):
            params = []
            for arg in fun.args.args:
                ann = arg.annotation
                annotation = inspect.Parameter.empty
                if isinstance(ann, ast.Constant):
                    annotation = ann.value
                elif isinstance(ann, ast.Name):
                    annotation = ann.id
                elif isinstance(ann, ast.Subscript):
                    data_type = eval(ann.slice.elts[0].id)
                    annotation = ann.slice.elts[1].value
                    annotation = Annotated[data_type, annotation]
                params.append(
                    inspect.Parameter(
                        arg.arg,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=annotation,
                    )
                )
            return inspect.Signature(
                params,
                return_annotation=fun.returns.value if not getattr(fun, "returns", False) else inspect._empty,
            )
        else:
            signature = inspect.signature(cls.couscous_func.get(name))
            return signature

    @classmethod
    def get_func(cls, name):
        return cls.couscous_func.get(name)

    def __init__(self, fun) -> None:

        self.nested_flag = False

        # For class decorators
        if isinstance(fun, type):
            method_list = [
                getattr(fun, func) for func in dir(fun) if callable(getattr(fun, func)) and not func.startswith("__")
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
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    if decorator.func.id == "couscous":
                        for kw in decorator.keywords:
                            if hasattr(kw, "value"):
                                if kw.arg == "ignore" and kw.value.value:  # type: ignore
                                    self.couscous_func.pop(node.name, False)
                                    return node

        if (fun := self.get_func(node.name)) is not None:
            self.nested_flag = True
            self.fun = fun
            self.fun_globals = fun.__globals__
            self.vars = {}
            if getattr(self, "class_attr", False):
                self.vars.update(self.class_attr)
        elif self.nested_flag:
            self.add_func(node)
        else:
            return node

        # Adding all annotations from own module
        annotations = getattr(sys.modules[self.fun.__module__], "__annotations__", None)
        if annotations is not None:
            for name, anno in annotations.items():
                if is_annotated(anno):
                    self.vars[name] = anno.__metadata__[0]
                if isinstance(anno, str):
                    self.vars[name] = anno

        # Adding all annotations from imported modules
        for _, val in self.fun_globals.items():
            if isinstance(val, types.ModuleType):
                annotations = getattr(val, "__annotations__", None)
                if annotations is not None:
                    for name, anno in annotations.items():
                        if is_annotated(anno):
                            self.vars[name] = anno.__metadata__[0]
                        if isinstance(anno, str):
                            self.vars[name] = anno

        # from function signature
        for arg in node.args.args:
            if arg.annotation is not None:
                anno_unit = get_annotation_unit(arg.annotation)
                if anno_unit in self.ureg:
                    self.vars[arg.arg] = anno_unit
                else:
                    _log.warning(
                        f"In function {self.fun.__module__}/{self.fun.__name__}: "
                        "Signature of couscoussed functions must be of type string or typing.Annotated"
                    )

        # Check units in the return node
        self.generic_visit(node)
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
            return QuantityNode(node, None)
        if isinstance(node, ast.Subscript):
            return QuantityNode(node, self.get_node_unit(node.value).unit)
        elif isinstance(node, ast.Tuple):
            elems = list(map(self.get_node_unit, node.elts))
            return QuantityNode(
                ast.Tuple([elem.node for elem in elems], ctx=node.ctx),
                cast(Sequence[Unit], [elem.unit for elem in elems]),
            )
        elif isinstance(node, ast.List):
            if not node.elts:
                return QuantityNode(node, None)
            else:
                elems = list(map(self.get_node_unit, node.elts))
                return QuantityNode(
                    ast.List([elem.node for elem in elems], ctx=node.ctx),
                    cast(Sequence[Unit], [elem.unit for elem in elems]),
                )
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

        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            if left.unit is None or right.unit is None:
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(ast.copy_location(new_node, node), None)

            if pint.Unit(left.unit).is_compatible_with(pint.Unit(right.unit)):
                conv_value = pint.Unit(left.unit).from_(pint.Unit(right.unit)).m
                new_node = ast.BinOp(
                    left.node,
                    node.op,
                    ast.BinOp(right.node, ast.Mult(), ast.Constant(conv_value)),
                )
                return QuantityNode(ast.copy_location(new_node, node), left.unit)

            else:
                raise_node = raise_dim_error(pint.errors.DimensionalityError, right.unit, left.unit)
                ast.copy_location(raise_node, node)
                return QuantityNode(raise_node, "dimensionless")

        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)):
            left = self.get_node_unit(node.left)
            right = self.get_node_unit(node.right)

            if left.unit is None or right.unit is None:
                new_node = ast.BinOp(left.node, node.op, right.node)
                return QuantityNode(ast.copy_location(new_node, node), None)

            if pint.Unit(left.unit).is_compatible_with(pint.Unit(right.unit)):
                conv_value = pint.Unit(left.unit).from_(pint.Unit(right.unit)).m
                new_node = ast.BinOp(
                    left.node,
                    node.op,
                    ast.BinOp(right.node, ast.Mult(), ast.Constant(conv_value)),
                )
                unit = f"{left.unit}*{left.unit}" if isinstance(node.op, ast.Mult) else "dimensionless"
                return QuantityNode(ast.copy_location(new_node, node), unit)

            else:
                new_node = ast.BinOp(left.node, node.op, right.node)
                unit = f"{left.unit}*{right.unit}" if isinstance(node.op, ast.Mult) else f"{left.unit}/{right.unit}"
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

            new_node = ast.IfExp(test=node.test, body=body.node, orelse=orelse.node)

            if body.unit != orelse.unit:
                _log.warning(
                    f"In function {self.fun.__module__}/{self.fun.__name__}: Ternary operator with mixed units"
                )
                return QuantityNode(ast.copy_location(new_node, node), None)
            else:
                return QuantityNode(ast.copy_location(new_node, node), body.unit)

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                id = node.func.id
            elif isinstance(node.func, ast.Attribute):
                id = node.func.attr
            if id in self.couscous_func:
                signature = self.get_func_signature(id)
            else:
                signature = inspect.Signature()

            new_args = []
            offset = 0
            fun_signature = [kv[1] for kv in signature.parameters.items()]
            if fun_signature:
                for i, arg in enumerate(node.args):
                    if fun_signature[i].name == "self":
                        offset = 1
                    expected = fun_signature[i + offset].annotation
                    if is_annotated(expected):
                        expected = expected.__metadata__[0]

                    msg = (
                        f"In function {self.fun.__module__}/{self.fun.__name__}: "
                        f"Function {id} expected unit {expected} but received unitless quantity"
                    )
                    if (received := self.get_node_unit(arg).unit) is None:
                        if expected is not inspect._empty:
                            _log.warning(msg)
                        new_args.append(node.args[i])
                        continue
                    if received != expected:
                        if pint.Unit(received).is_compatible_with(pint.Unit(expected)):
                            conv_value = pint.Unit(expected).from_(pint.Unit(received)).m
                        else:
                            raise_node = raise_dim_error(
                                pint.errors.DimensionalityError,
                                received,
                                expected,
                            )
                            return QuantityNode(raise_node, "dimensionless")

                        new_arg = ast.BinOp(
                            node.args[i],
                            ast.Mult(),
                            ast.Constant(conv_value),
                        )
                        new_args.append(new_arg)
                    else:
                        new_args.append(node.args[i])

            new_node = (
                node
                if not new_args
                else ast.Call(
                    func=node.func,
                    args=new_args,
                    keywords=node.keywords,
                )
            )

            return_val = signature.return_annotation if signature.return_annotation is not inspect._empty else None
            return QuantityNode(ast.copy_location(new_node, node), return_val)

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
                return node

            parameters = inspect.getfullargspec(self.fun_globals[node.func.id])
            new_args: list[ast.BinOp | ast.expr] = []
            for i, arg in enumerate(parameters.args):
                if (received := self.get_node_unit(node.args[i]).unit) != (expected := parameters.annotations[arg]):
                    if pint.Unit(received).is_compatible_with(pint.Unit(expected)):
                        conv_value = pint.Unit(expected).from_(pint.Unit(received)).m
                    else:
                        raise_node = raise_dim_error(pint.errors.DimensionalityError, received, expected)
                        return raise_node

                    new_arg = ast.BinOp(
                        node.args[i],
                        ast.Mult(),
                        ast.Constant(conv_value),
                    )
                    new_args.append(new_arg)
                else:
                    new_args.append(node.args[i])
            if new_args:
                new_node = ast.Call(
                    func=node.func,
                    args=new_args,
                    keywords=node.keywords,
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

        elif (received := value.unit) != (expected := cast(annotation_node, node.annotation)):

            expected_unit = get_annotation_unit(expected)

            if received == "dimensionless":
                new_node = node
            elif pint.Unit(received).is_compatible_with(pint.Unit(expected_unit)):
                conv_value = pint.Unit(expected_unit).from_(pint.Unit(received)).m
                new_value = ast.BinOp(
                    node.value,
                    ast.Mult(),
                    ast.Constant(conv_value),
                )
                new_node = ast.AnnAssign(
                    target=node.target,
                    annotation=node.annotation,
                    value=new_value,
                    simple=node.simple,
                )

            else:
                raise_node = raise_dim_error(pint.errors.DimensionalityError, received, expected_unit)
                return raise_node
        else:
            new_node = node

        if isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name):
                if node.target.value.id == "self":
                    self.class_attr[node.target.attr] = value.unit
        else:
            if isinstance(node.target, ast.Name):
                annotation = get_annotation_unit(cast(annotation_node, node.annotation))
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

        if value.node != node.value:

            new_node = ast.Assign(
                targets=node.targets,
                value=value.node,
            )
            node = ast.copy_location(new_node, node)

        if isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Tuple):
                    if isinstance(node.value.func, ast.Name):
                        for i, elem in enumerate(target.elts):
                            if isinstance(elem, ast.Name):
                                self.vars[elem.id] = (
                                    inspect.signature(self.fun_globals[node.value.func.id])
                                    .return_annotation.__args__[i]
                                    .__forward_value__
                                )
                    else:
                        for i, elem in enumerate(target.elts):
                            if (
                                isinstance(node.value.func, ast.Attribute)
                                and isinstance(elem, ast.Name)
                                and isinstance(node.value.func.value, ast.Name)
                            ):
                                self.vars[elem.id] = (
                                    inspect.signature(
                                        getattr(
                                            self.fun_globals[node.value.func.value.id],
                                            node.value.func.attr,
                                        )
                                    )
                                    .return_annotation.__args__[i]
                                    .__forward_value__
                                )
                elif isinstance(target, ast.Name):
                    self.vars[target.id] = value.unit
                elif isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name):
                        if target.value.id == "self":
                            self.class_attr[target.attr] = value.unit
            new_node = node

        else:
            new_node = ast.Assign(
                targets=node.targets,
                value=value.node,
                type_comment=f"unit: {value.unit}",
            )
            for target in node.targets:
                if isinstance(target, ast.Tuple):
                    for i, elem in enumerate(target.elts):
                        if isinstance(elem, ast.Name):
                            self.vars[elem.id] = value.unit[i]

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
        return_annotation = self.get_func_signature(fun)
        value = self.get_node_unit(node.value)

        if value.node != node.value:
            new_node = ast.Return(value=value.node)
            node = ast.copy_location(new_node, node)

        if return_annotation is inspect._empty:
            _log.warning(f"In function {self.fun.__module__}/{self.fun.__name__}: Some return annotations are missing")

        if is_annotated(return_annotation):
            expected = return_annotation.__metadata__
        elif isinstance(return_annotation, str):
            expected = return_annotation
        else:
            _log.warning(
                f"In function {self.fun.__module__}/{self.fun.__name__}: "
                "Type of the return annotation not supported yet"
            )
            return node

        if (received := value.unit) != expected:
            if pint.Unit(received).is_compatible_with(pint.Unit(expected)):
                conv_value = pint.Unit(expected).from_(pint.Unit(received)).m
                new_value = ast.BinOp(
                    node.value,
                    ast.Mult(),
                    ast.Constant(conv_value),
                )
                new_node = ast.Return(value=new_value)

            else:
                raise_node = raise_dim_error(pint.errors.DimensionalityError, received, expected)
                return raise_node
        else:
            new_node = node

        return ast.copy_location(new_node, node)
