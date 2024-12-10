import sympy
from environment.action import (
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_NUMBER,
    Action,
    ActionInput,
    ActionOutput,
    ActionArgsMetaInfo,
    InvalidActionArgException,
    InvalidActionArgsException,
)
from environment.state import State

class DoubleChildAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_NODE,
            ACTION_ARG_TYPE_NUMBER,
            ACTION_ARG_TYPE_NUMBER,
        ])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        if len(input.args) != len(cls.metadata().arg_types):
            raise InvalidActionArgsException(f"Invalid action length: {len(input.args)}")

        return cls(
            input=input,
            parent_node_idx=input.args[0].value,
            arg1=input.args[1].value,
            arg2=input.args[2].value,
        )

    def __init__(self, input: ActionInput, parent_node_idx: int, arg1: int, arg2: int):
        self._input = input
        self._parent_node_idx = parent_node_idx
        self._arg1 = arg1
        self._arg2 = arg2

    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

class SimplifyAddAction(DoubleChildAction):

    def output(self, state: State) -> ActionOutput:
        parent_node_idx = self._parent_node_idx
        arg1 = self._arg1
        arg2 = self._arg2

        parent_node = state.get_node(parent_node_idx)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_node_idx}")
        if not isinstance(parent_node, sympy.Add):
            raise InvalidActionArgException(f"Invalid parent node type: {type(parent_node)}")
        if not isinstance(arg1, int):
            raise InvalidActionArgsException(f"Invalid arg1 type: {type(arg1)}")
        if arg1 == arg2:
            raise InvalidActionArgsException(f"Invalid arg2 type: {type(arg2)}")
        if arg1 < 0 or arg2 < 0:
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
        if arg1 > len(parent_node.args) or arg2 > len(parent_node.args):
            raise InvalidActionArgsException(
                f"Invalid arg1 or arg2 max value: {arg1}, {arg2} (max {len(parent_node.args)})")

        node1 = parent_node.args[arg1]
        node2 = parent_node.args[arg2]

        if not isinstance(node1, sympy.Expr):
            raise InvalidActionArgsException(f"Invalid node1 type: {type(node1)}")
        if not isinstance(node2, sympy.Expr):
            raise InvalidActionArgsException(f"Invalid node2 type: {type(node2)}")


        if node1 != -node2:
            raise InvalidActionArgsException(
                f"Invalid node1 or node2 value (should be the same expression with opposite values): {node1}, {node2}")

        new_args = [arg for i, arg in enumerate(parent_node.args) if i not in [arg1, arg2]]

        if not new_args:
            return ActionOutput(node_idx=parent_node_idx, new_node=sympy.Integer(0))
        if len(new_args) == 1:
            return ActionOutput(node_idx=parent_node_idx, new_node=new_args[0])
        return ActionOutput(node_idx=parent_node_idx, new_node=sympy.Add(*new_args))

class SwapAddAction(DoubleChildAction):

    def output(self, state: State) -> ActionOutput:
        parent_node_idx = self._parent_node_idx
        arg1 = self._arg1
        arg2 = self._arg2

        parent_node = state.get_node(parent_node_idx)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_node_idx}")
        if not isinstance(parent_node, sympy.Add):
            raise InvalidActionArgException(f"Invalid parent node type: {type(parent_node)}")
        if not isinstance(arg1, int) or not isinstance(arg2, int):
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 type: {type(arg1)}, {type(arg2)}")
        if arg1 < 0 or arg2 < 0:
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
        if arg1 >= len(parent_node.args) or arg2 >= len(parent_node.args):
            raise InvalidActionArgsException(
                f"Invalid arg1 or arg2 max value: {arg1}, {arg2} (max {len(parent_node.args) - 1})")

        new_args = list(parent_node.args)
        new_args[arg1], new_args[arg2] = new_args[arg2], new_args[arg1]

        return ActionOutput(node_idx=parent_node_idx, new_node=sympy.Add(*new_args))
