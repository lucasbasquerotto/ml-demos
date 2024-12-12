from utils.types import BaseNode, ActionArgType, ActionArgsMetaInfo, ActionOutput
from utils.types import (
    ActionOutput,
    NewPartialDefinitionActionOutput,
    NewDefinitionFromPartialActionOutput,
    NewDefinitionFromNodeActionOutput,
    ReplaceByDefinitionActionOutput,
    ExpandDefinitionActionOutput,
    PartialActionOutput)
from environment.state import State

###########################################################
######################## CONSTANTS ########################
###########################################################

ACTION_ARG_TYPE_PARTIAL_DEFINITION = 1
ACTION_ARG_TYPE_DEFINITION = 2
ACTION_ARG_TYPE_GLOBAL_EXPRESSION = 1
ACTION_ARG_TYPE_NODE = 4
ACTION_ARG_TYPE_NUMBER = 5

ARG_TYPES = [
    ACTION_ARG_TYPE_PARTIAL_DEFINITION,
    ACTION_ARG_TYPE_DEFINITION,
    ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_NUMBER,
]

###########################################################
####################### EXCEPTIONS ########################
###########################################################

class InvalidActionException(Exception):
    pass

class InvalidActionArgException(InvalidActionException):
    pass

class InvalidActionArgsException(InvalidActionException):
    pass

###########################################################
######################### ACTION ##########################
###########################################################

class ActionArg:
    def __init__(self, type: ActionArgType, value: int):
        if type not in ARG_TYPES:
            raise InvalidActionArgException(f"Invalid action arg type: {type}")
        if not isinstance(value, int):
            raise InvalidActionArgException(f"Invalid action arg value: {value}")
        self._type = type
        self._value = value

    @property
    def type(self) -> ActionArgType:
        return self._type

    @property
    def value(self) -> int:
        return self._value

class ActionInput:
    def __init__(self, args: list[ActionArg]):
        self.args = args

class Action:

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        raise NotImplementedError()

    @classmethod
    def validate_args_amount(cls, input: ActionInput) -> None:
        if len(input.args) != len(cls.metadata().arg_types):
            raise InvalidActionArgsException(f"Invalid action length: {len(input.args)}")

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

    @property
    def input(self) -> ActionInput:
        raise NotImplementedError()

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

###########################################################
################### BASE IMPLEMENTATION ###################
###########################################################

class EmptyArgsBaseAction(Action):

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

class SingleExprBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([ACTION_ARG_TYPE_GLOBAL_EXPRESSION])

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

class DefinitionNodeBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_DEFINITION,
            ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
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

###########################################################
################## IMPLEMENTATION (MAIN) ##################
###########################################################

class NewDefinitionAction(EmptyArgsBaseAction):

    def output(self, state: State) -> ActionOutput:
        partial_definition_idx = len(state.partial_definitions or [])
        return NewPartialDefinitionActionOutput(partial_definition_idx=partial_definition_idx)

class NewDefinitionFromPartialAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([ACTION_ARG_TYPE_PARTIAL_DEFINITION])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            partial_definition_idx=input.args[0].value,
        )

    def __init__(self, input: ActionInput, partial_definition_idx: int):
        self._input = input
        self._partial_definition_idx = partial_definition_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        partial_definition_idx = self.partial_definition_idx
        partial_definitions = list(state.partial_definitions or [])
        if partial_definition_idx < 0 or partial_definition_idx >= len(partial_definitions):
            raise InvalidActionArgException(
                f"Invalid partial definition index: {partial_definition_idx}")
        _, partial_definition = partial_definitions[partial_definition_idx]
        if not partial_definition:
            raise InvalidActionArgException(
                f"Partial definition {partial_definition_idx} has no expression")
        definition_idx = len(state.definitions or [])
        return NewDefinitionFromPartialActionOutput(
            definition_idx=definition_idx,
            partial_definition_idx=partial_definition_idx)

class NodeToDefinitionAction(SingleExprBaseAction):

    def output(self, state: State) -> ActionOutput:
        expr_id = self.expr_id
        node = state.get_node(expr_id)
        if not node:
            raise InvalidActionArgException(f"Invalid node index: {expr_id}")
        definition_idx = len(state.definitions or [])
        return NewDefinitionFromNodeActionOutput(
            definition_idx=definition_idx,
            expr_id=expr_id)

class ReplaceByDefinitionAction(DefinitionNodeBaseAction):

    def output(self, state: State) -> ActionOutput:
        definition_idx = self.definition_idx
        expr_id = self.expr_id
        definitions = state.definitions
        if definitions is None:
            raise InvalidActionArgException("No definitions yet")
        if definition_idx < 0 or definition_idx >= len(state.definitions or []):
            raise InvalidActionArgException(f"Invalid definition index: {definition_idx}")
        key, definition_node = definitions[definition_idx]
        target_node = state.get_node(expr_id)
        if not target_node:
            raise InvalidActionArgException(f"Invalid target node index: {expr_id}")
        if definition_node != target_node:
            raise InvalidActionArgException(
                f"Invalid target node: {target_node} "
                + f"(expected {definition_node} from definition {key})")
        return ReplaceByDefinitionActionOutput(definition_idx=definition_idx, expr_id=expr_id)

class ExpandDefinitionAction(DefinitionNodeBaseAction):

    def output(self, state: State) -> ActionOutput:
        definition_idx = self.definition_idx
        expr_id = self.expr_id
        definitions = state.definitions
        if definitions is None:
            raise InvalidActionArgException("No definitions yet")
        if definition_idx < 0 or definition_idx >= len(state.definitions or []):
            raise InvalidActionArgException(f"Invalid definition index: {definition_idx}")
        key, definition_node = definitions[definition_idx]
        if not definition_node:
            raise InvalidActionArgException(f"Definition {definition_idx} has no expression")
        target_node = state.get_node(expr_id)
        if not target_node:
            raise InvalidActionArgException(f"Invalid target node index: {expr_id}")
        if key != target_node:
            raise InvalidActionArgException(
                f"Invalid target node: {target_node} (expected {key})")
        return ExpandDefinitionActionOutput(definition_idx=definition_idx, expr_id=expr_id)
