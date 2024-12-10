from environment.action import (
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_NUMBER,
    Action,
    ActionInput,
    ActionOutput,
    ActionArgsMetaInfo,
    InvalidActionArgsException,
)
from environment.state import State

class SingleNodeAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([ACTION_ARG_TYPE_NODE])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        if len(input.args) != len(cls.metadata().arg_types):
            raise InvalidActionArgsException(f"Invalid action length: {len(input.args)}")

        return cls(
            input=input,
            node_idx=input.args[0].value,
        )

    def __init__(self, input: ActionInput, node_idx: int):
        self._input = input
        self._node_idx = node_idx

    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

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
