import sympy
from utils.types import BaseNode, NodeTypeHandler, DefinitionKey

definition_handler = NodeTypeHandler(
    DefinitionKey,
    lambda params: params.definition_keys.index(params.node))
symbol_handler = NodeTypeHandler(BaseNode, lambda params: params.symbols.index(params.node))
integer_handler = NodeTypeHandler(sympy.Integer, lambda params: int(params.node))
