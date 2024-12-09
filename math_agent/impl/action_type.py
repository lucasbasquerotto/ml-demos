import sympy
from environment.action import (
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_NUMBER,
    Action,
    ActionArgsMetaInfo,
    InvalidActionArgException,
    InvalidActionArgsException,
)
from environment.state import BaseNode, State
from utils.logger import logger

class SimplifyAddAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_NODE,
            ACTION_ARG_TYPE_NUMBER,
            ACTION_ARG_TYPE_NUMBER,
        ])

    @classmethod
    def from_raw_action(cls, action: tuple[int, ...]) -> 'SimplifyAddAction':
        if len(action) != len(cls.metadata().arg_types):
            logger.error(f"Invalid action length: {len(action)}")
            raise InvalidActionArgsException()

        return cls(
            parent_node_idx=action[0],
            arg1=action[1],
            arg2=action[2],
        )

    def __init__(self, parent_node_idx: int, arg1: int, arg2: int):
        self._parent_node_idx = parent_node_idx
        self._arg1 = arg1
        self._arg2 = arg2

    def apply(self, state: State) -> State:
        parent_node_idx = self._parent_node_idx
        arg1 = self._arg1
        arg2 = self._arg2

        parent_node = state.get_node(parent_node_idx)

        if not parent_node:
            logger.error(f"Invalid parent node index: {parent_node_idx}")
            raise InvalidActionArgException()
        if not isinstance(parent_node, sympy.Add):
            logger.error(f"Invalid parent node type: {type(parent_node)}")
            raise InvalidActionArgException()
        if not isinstance(arg1, int):
            logger.error(f"Invalid arg1 type: {type(arg1)}")
            raise InvalidActionArgsException()
        if arg1 == arg2:
            logger.error(f"Invalid arg2 type: {type(arg2)}")
            raise InvalidActionArgsException()
        if arg1 < 0 or arg2 < 0:
            logger.error(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
            raise InvalidActionArgsException()
        if arg1 > len(parent_node.args) or arg2 > len(parent_node.args):
            logger.error(
                f"Invalid arg1 or arg2 max value: {arg1}, {arg2} (max {len(parent_node.args)})")
            raise InvalidActionArgsException()

        node1 = parent_node.args[arg1]
        node2 = parent_node.args[arg2]

        if not isinstance(node1, BaseNode):
            logger.error(f"Invalid node1 type: {type(node1)}")
            raise InvalidActionArgsException()
        if not isinstance(node2, BaseNode):
            logger.error(f"Invalid node2 type: {type(node2)}")
            raise InvalidActionArgsException()

        if node1 != node2:
            logger.error(
                f"Invalid node1 or node2 value (should be the same expression): {node1}, {node2}")
            raise InvalidActionArgsException()

        new_args = [arg for i, arg in enumerate(parent_node.args) if i not in [arg1, arg2]]

        if not new_args:
            return state.replace_node(parent_node_idx, sympy.Integer(0))
        if len(new_args) == 1:
            return state.replace_node(parent_node_idx, new_args[0])
        return state.replace_node(parent_node_idx, sympy.Add(*new_args))
