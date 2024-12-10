import sympy

BaseNode = sympy.Basic

class DefinitionKey(sympy.Dummy):
    pass

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

class NodeActionOutput:
    def __init__(self, node_idx: int, new_node: BaseNode):
        self._node_idx = node_idx
        self._new_node = new_node

    @property
    def node_idx(self) -> int:
        return self._node_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

class NewDefinitionActionOutput:
    def __init__(self, definition_idx: int, node_idx: int | None):
        self._definition_idx = definition_idx
        self._node_idx = node_idx

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def node_idx(self) -> int | None:
        return self._node_idx

ActionOutput = NodeActionOutput | NewDefinitionActionOutput
