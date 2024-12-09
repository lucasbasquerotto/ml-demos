from utils.types import BaseNode, ActionArgType, ActionArgsMetaInfo
from utils.logger import logger
from .state import State

ACTION_ARG_TYPE_NODE = 0
ACTION_ARG_TYPE_NUMBER = 1

class InvalidActionException(Exception):
    pass

class InvalidActionArgException(InvalidActionException):
    pass

class InvalidActionArgsException(InvalidActionException):
    pass

class ActionArg:
    def __init__(self, type: ActionArgType, value: int):
        if type not in [ACTION_ARG_TYPE_NODE, ACTION_ARG_TYPE_NUMBER]:
            logger.error(f"Invalid action arg type: {type}")
            raise InvalidActionArgException()
        if not isinstance(value, int):
            logger.error(f"Invalid action arg value: {value}")
            raise InvalidActionArgException()
        self._type = type
        self._value = value

    def get_node(self, state: State) -> BaseNode:
        if self._type != ACTION_ARG_TYPE_NODE:
            logger.error(f"Invalid action arg type: {self._type} (expected {ACTION_ARG_TYPE_NODE})")
            raise InvalidActionArgException()
        node = state.get_node(self._value)
        if not node:
            logger.error(f"Invalid node index: {self._value}")
            raise InvalidActionArgException()
        return node

    def get_number(self) -> int:
        if self._type != ACTION_ARG_TYPE_NUMBER:
            logger.error(
                f"Invalid action arg type: {self._type} (expected {ACTION_ARG_TYPE_NUMBER})")
            raise InvalidActionArgException()
        return self._value

class Action:

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        raise NotImplementedError()

    @classmethod
    def from_raw_action(cls, action: tuple[int, ...]) -> 'Action':
        raise NotImplementedError()

    def apply(self, state: State) -> State:
        raise NotImplementedError()
