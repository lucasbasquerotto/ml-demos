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
        self.arg_types = arg_types

class ActionOutput:
    def __init__(self, node_idx: int, new_node: BaseNode):
        self.node_idx = node_idx
        self.new_node = new_node
