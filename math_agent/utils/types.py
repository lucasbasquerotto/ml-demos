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

class NewPartialDefinitionActionOutput:
    def __init__(self, partial_definition_idx: int):
        self._partial_definition_idx = partial_definition_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

class NewDefinitionFromPartialActionOutput:
    def __init__(self, definition_idx: int, partial_definition_idx: int):
        self._definition_idx = definition_idx
        self._partial_definition_idx = partial_definition_idx

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

class NewDefinitionFromNodeActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class ReplaceByDefinitionActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class ApplyDefinitionActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class SameValueNodeActionOutput:
    def __init__(self, expr_id: int, new_node: BaseNode):
        self._expr_id = expr_id
        self._new_node = new_node

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

class UpdatePartialDefinitionActionOutput:
    def __init__(self, partial_definition_idx: int, new_node: BaseNode):
        self._partial_definition_idx = partial_definition_idx
        self._new_node = new_node

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

ActionOutput = (
    NewPartialDefinitionActionOutput |
    NewDefinitionFromPartialActionOutput |
    NewDefinitionFromNodeActionOutput |
    ApplyDefinitionActionOutput |
    SameValueNodeActionOutput |
    UpdatePartialDefinitionActionOutput)
