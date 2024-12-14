import sympy
from environment.action import (
    ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
    ACTION_ARG_TYPE_INT,
    Action,
    ActionInput,
    ActionArgsMetaInfo,
    InvalidActionArgException,
    InvalidActionArgsException,
    ReformulationActionOutput,
)
from environment.state import State
from impl import node_types

###########################################################
################### BASE IMPLEMENTATION ###################
###########################################################

class DoubleChildReformulationBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo((
            ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
            ACTION_ARG_TYPE_INT,
            ACTION_ARG_TYPE_INT,
        ))

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            parent_expr_id=input.args[0].value,
            arg1=input.args[1].value,
            arg2=input.args[2].value,
        )

    def __init__(self, input: ActionInput, parent_expr_id: int, arg1: int, arg2: int):
        self._input = input
        self._parent_expr_id = parent_expr_id
        self._arg1 = arg1
        self._arg2 = arg2

    @property
    def parent_expr_id(self) -> int:
        return self._parent_expr_id

    @property
    def arg1(self) -> int:
        return self._arg1

    @property
    def arg2(self) -> int:
        return self._arg2

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ReformulationActionOutput:
        raise NotImplementedError()

###########################################################
##################### IMPLEMENTATION ######################
###########################################################

class SimplifyAddAction(DoubleChildReformulationBaseAction):

    def output(self, state: State) -> ReformulationActionOutput:
        parent_expr_id = self.parent_expr_id
        arg1 = self.arg1
        arg2 = self.arg2

        parent_node = state.get_node(parent_expr_id)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_expr_id}")
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
                "Invalid node1 or node2 value "
                + "(should be the same expression with opposite values): "
                + f"{node1}, {node2}")

        new_args = [arg for i, arg in enumerate(parent_node.args) if i not in [arg1, arg2]]

        if not new_args:
            return ReformulationActionOutput(expr_id=parent_expr_id, new_node=sympy.Integer(0))
        if len(new_args) == 1:
            return ReformulationActionOutput(expr_id=parent_expr_id, new_node=new_args[0])
        return ReformulationActionOutput(expr_id=parent_expr_id, new_node=sympy.Add(*new_args))

class SwapAddAction(DoubleChildReformulationBaseAction):

    def output(self, state: State) -> ReformulationActionOutput:
        parent_expr_id = self.parent_expr_id
        arg1 = self._arg1
        arg2 = self._arg2

        parent_node = state.get_node(parent_expr_id)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_expr_id}")
        if not isinstance(parent_node, node_types.Add):
            raise InvalidActionArgException(f"Invalid parent node type: {type(parent_node)}")
        if not isinstance(arg1, int) or not isinstance(arg2, int):
            raise InvalidActionArgsException(
                f"Invalid arg1 or arg2 type: {type(arg1)}, {type(arg2)}")
        if arg1 < 0 or arg2 < 0:
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
        if arg1 >= len(parent_node.args) or arg2 >= len(parent_node.args):
            raise InvalidActionArgsException(
                "Invalid arg1 or arg2 max value: "
                + f"{arg1}, {arg2} (max {len(parent_node.args) - 1})")

        new_args = list(parent_node.args)
        new_args[arg1], new_args[arg2] = new_args[arg2], new_args[arg1]

        return ReformulationActionOutput(expr_id=parent_expr_id, new_node=node_types.Add(*new_args))
