from typing import Callable, Generic, Type, TypeVar
# from sympy.logic.boolalg import Boolean
import sympy

BaseNode = sympy.Basic

T = TypeVar("T", bound=BaseNode)
V = TypeVar("V", bound=int | float)

DefinitionKey = sympy.Dummy

Assumption = sympy.Basic

class NodeValueParams(Generic[T]):
    def __init__(self, node: T, symbols: list[BaseNode], definition_keys: list[DefinitionKey]):
        self.node = node
        self.symbols = symbols
        self.definition_keys = definition_keys

class NodeTypeHandler(Generic[T, V]):
    def __init__(
        self,
        node_type: Type[T],
        get_value: Callable[[NodeValueParams[T]], V],
    ):
        self.node_type = node_type
        self.get_value = get_value

ACTION_ARG_TYPE_NODE = 0
ACTION_ARG_TYPE_NUMBER = 1

ActionArgType = int

class ActionArgsMetaInfo:
    def __init__(
        self,
        arg_types: list[ActionArgType],
    ):
        self.arg_types = arg_types