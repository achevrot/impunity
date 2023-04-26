# import ast


# class AstRaise(ast.NodeTransformer):
#     def get_node(self, except_name: str) -> ast.Raise:
#         mod = ast.parse(f"raise {except_name}")
#         self.generic_visit(mod)
#         return self.exception

#     def visit_Raise(self, node: ast.Raise):
#         self.exception = node


# def raise_dim_error(e, received, expected):
#     exception = e.__module__ + "." + e.__qualname__
#       + f'("{received}", "{expected}")'
#     new_node = AstRaise().get_node(exception)
#     return new_node
