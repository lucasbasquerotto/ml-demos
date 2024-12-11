from environment.action import (
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_DEFINITION,
    ACTION_ARG_TYPE_PARTIAL_DEFINITION,
    ACTION_ARG_TYPE_NUMBER,
    Action,
    ActionInput,
    ActionOutput,
    ActionArgsMetaInfo,
)
from environment.state import State

class EmptyArgsAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(input=input)

    def __init__(self, input: ActionInput):
        self._input = input

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

class SingleNodeAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([ACTION_ARG_TYPE_NODE])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            expr_id=input.args[0].value,
        )

    def __init__(self, input: ActionInput, expr_id: int):
        self._input = input
        self._expr_id = expr_id

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

class PartialDefinitionNodeChangeAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_PARTIAL_DEFINITION,
            ACTION_ARG_TYPE_NODE,
        ])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            partial_definition_idx=input.args[0].value,
            expr_id=input.args[1].value,
        )

    def __init__(self, input: ActionInput, partial_definition_idx: int, expr_id: int):
        self._input = input
        self._partial_definition_idx = partial_definition_idx
        self._expr_id = expr_id

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

class DefinitionNodeAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_DEFINITION,
            ACTION_ARG_TYPE_NODE,
        ])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            definition_idx=input.args[0].value,
            expr_id=input.args[1].value,
        )

    def __init__(self, input: ActionInput, definition_idx: int, expr_id: int):
        self._input = input
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
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

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()
