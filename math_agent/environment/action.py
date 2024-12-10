from utils.types import BaseNode, ActionArgType, ActionArgsMetaInfo, ActionOutput
from .state import State

ACTION_ARG_TYPE_NODE = 1
ACTION_ARG_TYPE_NUMBER = 2

class InvalidActionException(Exception):
    pass

class InvalidActionArgException(InvalidActionException):
    pass

class InvalidActionArgsException(InvalidActionException):
    pass

class ActionArg:
    def __init__(self, type: ActionArgType, value: int):
        if type not in [ACTION_ARG_TYPE_NODE, ACTION_ARG_TYPE_NUMBER]:
            raise InvalidActionArgException(f"Invalid action arg type: {type}")
        if not isinstance(value, int):
            raise InvalidActionArgException(f"Invalid action arg value: {value}")
        self.type = type
        self.value = value

    def get_node(self, state: State) -> BaseNode:
        if self.type != ACTION_ARG_TYPE_NODE:
            raise InvalidActionArgException(
                f"Invalid action arg type: {self.type} (expected {ACTION_ARG_TYPE_NODE})")
        node = state.get_node(self.value)
        if not node:
            raise InvalidActionArgException(f"Invalid node index: {self.value}")
        return node

    def get_number(self) -> int:
        if self.type != ACTION_ARG_TYPE_NUMBER:
            raise InvalidActionArgException(
                f"Invalid action arg type: {self.type} (expected {ACTION_ARG_TYPE_NUMBER})")
        return self.value

class ActionInput:
    def __init__(self, args: list[ActionArg]):
        self.args = args

class Action:

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        raise NotImplementedError()

    @classmethod
    def to_input(cls, action: tuple[int, ...]) -> ActionInput:
        if len(action) != len(cls.metadata().arg_types):
            raise InvalidActionArgsException(f"Invalid action length: {len(action)}")

        args = [
            ActionArg(type, value)
            for type, value in zip(cls.metadata().arg_types, action)
        ]
        return ActionInput(args)

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        raise NotImplementedError()

    def input(self) -> ActionInput:
        raise NotImplementedError()

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()
