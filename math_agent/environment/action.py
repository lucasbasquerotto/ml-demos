from utils.types import BaseNode, DefinitionKey
from environment.state import State

###########################################################
######################## CONSTANTS ########################
###########################################################

ACTION_ARG_TYPE_PARTIAL_DEFINITION = 1
ACTION_ARG_TYPE_DEFINITION = 2
ACTION_ARG_TYPE_GLOBAL_EXPRESSION = 3
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
###################### ACTION INPUT #######################
###########################################################

ActionArgType = int

class ActionArgsMetaInfo:
    def __init__(
        self,
        arg_types: tuple[ActionArgType, ...],
    ):
        self._arg_types = arg_types

    @property
    def arg_types(self) -> tuple[ActionArgType, ...]:
        return self._arg_types

class ActionMetaInfo(ActionArgsMetaInfo):
    def __init__(
        self,
        type_idx: int,
        arg_types: tuple[ActionArgType, ...],
    ):
        super().__init__(arg_types=arg_types)
        self._type_idx = type_idx

    @property
    def type_idx(self) -> int:
        return self._type_idx

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
    def __init__(self, args: tuple[ActionArg, ...]):
        self.args = args

###########################################################
###################### ACTION OUTPUT ######################
###########################################################

class NewPartialDefinitionActionOutput:
    def __init__(self, partial_definition_idx: int):
        self._partial_definition_idx = partial_definition_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

class NewDefinitionFromPartialActionOutput:
    def __init__(self, definition_idx: int, partial_definition_idx: int):
        self._definition_idx = definition_idx
        self._partial_definition_idx = partial_definition_idx

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

class NewDefinitionFromNodeActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class ReplaceByDefinitionActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class ExpandDefinitionActionOutput:
    def __init__(self, definition_idx: int, expr_id: int):
        self._definition_idx = definition_idx
        self._expr_id = expr_id

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

class ReformulationActionOutput:
    def __init__(self, expr_id: int, new_node: BaseNode):
        self._expr_id = expr_id
        self._new_node = new_node

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

class PartialActionOutput:
    def __init__(self, partial_definition_idx: int, node_idx: int, new_node: BaseNode):
        self._partial_definition_idx = partial_definition_idx
        self._node_idx = node_idx
        self._new_node = new_node

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def node_idx(self) -> int:
        return self._node_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

ActionOutput = (
    NewPartialDefinitionActionOutput |
    NewDefinitionFromPartialActionOutput |
    NewDefinitionFromNodeActionOutput |
    ReplaceByDefinitionActionOutput |
    ExpandDefinitionActionOutput |
    ReformulationActionOutput |
    PartialActionOutput)

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
        return ActionInput(tuple(args))

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        raise NotImplementedError()

    @property
    def input(self) -> ActionInput:
        raise NotImplementedError()

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

    def apply(self, state: State) -> 'State':
        output = self.output(state)

        if isinstance(output, NewPartialDefinitionActionOutput):
            partial_definition_idx = output.partial_definition_idx

            assert partial_definition_idx == len(state.partial_definitions or []), \
                f"Invalid partial definition index: {partial_definition_idx}"

            partial_definitions = list(state.partial_definitions or [])
            partial_definitions.append((DefinitionKey(), None))

            return State(
                expression=state.expression,
                definitions=state.definitions,
                partial_definitions=tuple(partial_definitions),
                assumptions=state.assumptions)
        elif isinstance(output, NewDefinitionFromPartialActionOutput):
            definition_idx = output.definition_idx
            assert definition_idx == len(state.definitions or []), \
                f"Invalid definition index: {definition_idx}"

            partial_definition_idx = output.partial_definition_idx
            assert partial_definition_idx is not None, "Empty partial definition index"
            assert partial_definition_idx >= 0, \
                f"Invalid partial definition index: {partial_definition_idx}"
            assert partial_definition_idx < len(state.partial_definitions or []), \
                f"Invalid partial definition index: {partial_definition_idx}"

            partial_definitions_list = list(state.partial_definitions or [])
            key, expr = partial_definitions_list[partial_definition_idx]
            assert expr is not None, "Empty expression for partial definition"

            definitions_list = list(state.definitions or [])
            definitions_list.append((key, expr))

            partial_definitions_list = [
                (key, expr)
                for i, (key, expr) in enumerate(partial_definitions_list)
                if i != partial_definition_idx
            ]

            return State(
                expression=state.expression,
                definitions=tuple(definitions_list),
                partial_definitions=tuple(partial_definitions_list),
                assumptions=state.assumptions)
        elif isinstance(output, NewDefinitionFromNodeActionOutput):
            definition_idx = output.definition_idx
            assert definition_idx == len(state.definitions or []), \
                f"Invalid definition index: {definition_idx}"

            action_expr_id = output.expr_id
            assert action_expr_id is not None, "Empty expression id"
            assert action_expr_id > 0, f"Invalid expression id: {action_expr_id}"
            action_node_idx = action_expr_id - 1
            node = state.get_node(action_node_idx)
            assert node is not None, f"Invalid node index: {action_node_idx}"

            definitions_list = list(state.definitions or [])
            definitions_list.append((DefinitionKey(), node))

            return State(
                expression=state.expression,
                definitions=tuple(definitions_list),
                partial_definitions=state.partial_definitions,
                assumptions=state.assumptions)
        elif isinstance(output, ReplaceByDefinitionActionOutput):
            definition_idx = output.definition_idx
            expr_id = output.expr_id
            definitions = state.definitions

            assert definitions is not None, "No definitions yet"
            assert definition_idx is not None, "Empty definition index"
            assert definition_idx >= 0, f"Invalid definition index: {definition_idx}"
            assert definition_idx < len(definitions), \
                f"Invalid definition index: {definition_idx}"
            assert expr_id is not None, "Empty expression id"

            key, definition_node = definitions[definition_idx]
            target_node = state.get_node(expr_id)
            assert definition_node == target_node, \
                f"Invalid definition node: {definition_node} (expected {target_node})"

            return state.apply_new_node(expr_id=expr_id, new_node=key)
        elif isinstance(output, ExpandDefinitionActionOutput):
            definition_idx = output.definition_idx
            expr_id = output.expr_id
            definitions = state.definitions

            assert definitions is not None, "No definitions yet"
            assert definition_idx is not None, "Empty definition index"
            assert definition_idx >= 0, f"Invalid definition index: {definition_idx}"
            assert definition_idx < len(definitions), \
                f"Invalid definition index: {definition_idx}"
            assert expr_id is not None, "Empty expression id"

            key, definition_node = definitions[definition_idx]
            target_node = state.get_node(expr_id)
            assert key == target_node, f"Invalid target node: {target_node} (expected {key})"

            return state.apply_new_node(expr_id=expr_id, new_node=definition_node)
        elif isinstance(output, ReformulationActionOutput):
            expr_id = output.expr_id
            new_node = output.new_node
            return state.apply_new_node(expr_id=expr_id, new_node=new_node)
        elif isinstance(output, PartialActionOutput):
            partial_definition_idx = output.partial_definition_idx
            node_idx = output.node_idx
            new_node = output.new_node
            partial_definitions_list = list(state.partial_definitions or [])

            assert partial_definition_idx is not None, "Empty partial definition index"
            assert partial_definition_idx >= 0, \
                f"Invalid partial definition index: {partial_definition_idx}"
            assert partial_definition_idx < len(partial_definitions_list), \
                f"Invalid partial definition index: {partial_definition_idx}"

            key, _ = partial_definitions_list[partial_definition_idx]
            partial_definitions_list[partial_definition_idx] = (key, new_node)

            return state.change_partial_definition(
                partial_definition_idx=partial_definition_idx,
                node_idx=node_idx,
                new_node=new_node)
        else:
            raise ValueError(f"Invalid action output: {output}")

###########################################################
################### BASE IMPLEMENTATION ###################
###########################################################

class EmptyArgsBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo(tuple())

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
        return ActionArgsMetaInfo((ACTION_ARG_TYPE_GLOBAL_EXPRESSION,))

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
        return ActionArgsMetaInfo((
            ACTION_ARG_TYPE_DEFINITION,
            ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
        ))

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

class NewPartialDefinitionAction(EmptyArgsBaseAction):

    def output(self, state: State) -> ActionOutput:
        partial_definition_idx = len(state.partial_definitions or [])
        return NewPartialDefinitionActionOutput(partial_definition_idx=partial_definition_idx)

class NewDefinitionFromPartialAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo((ACTION_ARG_TYPE_PARTIAL_DEFINITION,))

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

class NewDefinitionFromNodeAction(SingleExprBaseAction):

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

DEFAULT_ACTIONS = [
    NewPartialDefinitionAction,
    NewDefinitionFromPartialAction,
    NewDefinitionFromNodeAction,
    ReplaceByDefinitionAction,
    ExpandDefinitionAction,
]
