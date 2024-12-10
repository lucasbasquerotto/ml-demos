import sympy
from environment.meta_env import NodeTypeHandler

definition_handler = NodeTypeHandler(
    sympy.Dummy,
    lambda params: params.definition_keys.index(params.node))

symbol_handler = NodeTypeHandler(sympy.Symbol, lambda params: params.symbols.index(params.node))

integer_handler = NodeTypeHandler(sympy.Integer, lambda params: int(params.node))
