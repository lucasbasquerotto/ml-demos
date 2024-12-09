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
