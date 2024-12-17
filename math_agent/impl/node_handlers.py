import typing
import sympy
from utils.types import FunctionDefinition
from environment.meta_env import NodeTypeHandler, BaseNode

T = typing.TypeVar("T", bound=BaseNode)
V = typing.TypeVar("V", bound=int | float)

definition_handler = NodeTypeHandler(
    FunctionDefinition,
    lambda params: params.definition_keys.index(params.node))

symbol_handler = NodeTypeHandler(sympy.Symbol, lambda params: params.symbols.index(params.node))

integer_handler = NodeTypeHandler(sympy.Integer, lambda params: int(params.node))
