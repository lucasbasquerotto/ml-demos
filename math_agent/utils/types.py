import sympy

BaseNode = sympy.Basic

DefinitionKey = sympy.Dummy

Assumption = sympy.Basic

ActionArgType = int

class ActionArgsMetaInfo:
    def __init__(
        self,
        arg_types: list[ActionArgType],
    ):
        self._arg_types = arg_types

    @property
    def arg_types(self) -> list[ActionArgType]:
        return self._arg_types

class ActionOutput:
    def __init__(self, node_idx: int, new_node: BaseNode):
        self._node_idx = node_idx
        self._new_node = new_node

    @property
    def node_idx(self) -> int:
        return self._node_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node
