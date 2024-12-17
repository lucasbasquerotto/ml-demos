from utils.types import BaseNode, FunctionDefinition
from environment.state import State, ArgGroup

###########################################################
######################## CONSTANTS ########################
###########################################################

ACTION_ARG_TYPE_PARTIAL_DEFINITION = 1
ACTION_ARG_TYPE_ARG_GROUP = 2
ACTION_ARG_TYPE_ARG_IDX = 3
ACTION_ARG_TYPE_DEFINITION = 4
ACTION_ARG_TYPE_GLOBAL_EXPRESSION = 5
ACTION_ARG_TYPE_NODE = 6
ACTION_ARG_TYPE_INT = 7

ARG_TYPES = [
    ACTION_ARG_TYPE_PARTIAL_DEFINITION,
    ACTION_ARG_TYPE_DEFINITION,
    ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
    ACTION_ARG_TYPE_NODE,
    ACTION_ARG_TYPE_INT,
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

class NewArgGroupActionOutput:
    def __init__(self, arg_group_idx: int, amount: int):
        self._arg_group_idx = arg_group_idx
        self._amount = amount

    @property
    def arg_group_idx(self) -> int:
        return self._arg_group_idx

    @property
    def amount(self) -> int:
        return self._amount

class ArgFromExprActionOutput:
    def __init__(self, arg_group_idx: int, arg_idx: int, new_node: BaseNode):
        self._arg_group_idx = arg_group_idx
        self._arg_idx = arg_idx
        self._new_node = new_node

    @property
    def arg_group_idx(self) -> int:
        return self._arg_group_idx

    @property
    def arg_idx(self) -> int:
        return self._arg_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

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

class NewDefinitionFromExprActionOutput:
    def __init__(self, definition_idx: int, new_node: BaseNode):
        self._definition_idx = definition_idx
        self._new_node = new_node

    @property
    def definition_idx(self) -> int:
        return self._definition_idx

    @property
    def new_node(self) -> BaseNode:
        return self._new_node

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
    NewArgGroupActionOutput |
    ArgFromExprActionOutput |
    NewDefinitionFromPartialActionOutput |
    NewDefinitionFromExprActionOutput |
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
            partial_definitions.append((FunctionDefinition(), None))

            return State(
                expression=state.expression,
                definitions=state.definitions,
                partial_definitions=tuple(partial_definitions),
                arg_groups=state.arg_groups,
                assumptions=state.assumptions)
        elif isinstance(output, NewArgGroupActionOutput):
            arg_group_idx = output.arg_group_idx
            amount = output.amount

            assert arg_group_idx == len(state.arg_groups or []), \
                f"Invalid arg group index: {arg_group_idx}"

            arg_groups = list(state.arg_groups or [])
            arg_groups.append(ArgGroup(amount=amount, expressions=tuple([None] * amount)))

            return State(
                expression=state.expression,
                definitions=state.definitions,
                partial_definitions=state.partial_definitions,
                arg_groups=tuple(arg_groups),
                assumptions=state.assumptions)
        elif isinstance(output, ArgFromExprActionOutput):
            arg_group_idx = output.arg_group_idx
            arg_idx = output.arg_idx
            new_node = output.new_node

            arg_groups = list(state.arg_groups or [])
            if len(arg_groups) == 0:
                raise InvalidActionArgException("No arg groups yet")
            if arg_group_idx < 0 or arg_group_idx >= len(arg_groups):
                raise InvalidActionArgException(f"Invalid arg group index: {arg_group_idx}")
            arg_group = arg_groups[arg_group_idx]
            if arg_idx < 0 or arg_idx >= arg_group.amount:
                raise InvalidActionArgException(f"Invalid arg index: {arg_idx}")

            arg_groups_list = list(arg_groups)
            arg_group_list = list(arg_group.expressions)
            arg_group_list[arg_idx] = new_node
            arg_groups_list[arg_group_idx] = ArgGroup(
                amount=arg_group.amount,
                expressions=tuple(arg_group_list))

            return State(
                expression=state.expression,
                definitions=state.definitions,
                partial_definitions=state.partial_definitions,
                arg_groups=tuple(arg_groups_list),
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
                arg_groups=state.arg_groups,
                assumptions=state.assumptions)
        elif isinstance(output, NewDefinitionFromExprActionOutput):
            definition_idx = output.definition_idx
            assert definition_idx == len(state.definitions or []), \
                f"Invalid definition index: {definition_idx}"

            new_node = output.new_node
            assert new_node is not None, "Invalid new node"

            definitions_list = list(state.definitions or [])
            definitions_list.append((FunctionDefinition(), new_node))

            return State(
                expression=state.expression,
                definitions=tuple(definitions_list),
                partial_definitions=state.partial_definitions,
                arg_groups=state.arg_groups,
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

class IntInputBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo((ACTION_ARG_TYPE_INT,))

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            value=input.args[0].value,
        )

    def __init__(self, input: ActionInput, value: int):
        self._input = input
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

class ArgFromExprBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo((
            ACTION_ARG_TYPE_ARG_GROUP,
            ACTION_ARG_TYPE_ARG_IDX,
            ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
        ))

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            arg_group_idx=input.args[0].value,
            arg_idx=input.args[1].value,
            expr_id=input.args[1].value,
        )

    def __init__(self, input: ActionInput, arg_group_idx: int, arg_idx: int, expr_id: int):
        self._input = input
        self._arg_group_idx = arg_group_idx
        self._arg_idx = arg_idx
        self._expr_id = expr_id

    @property
    def arg_group_idx(self) -> int:
        return self._arg_group_idx

    @property
    def arg_idx(self) -> int:
        return self._arg_idx

    @property
    def expr_id(self) -> int:
        return self._expr_id

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ArgFromExprActionOutput:
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

class DefinitionExprBaseAction(Action):

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

class NewArgGroupAction(IntInputBaseAction):

    def output(self, state: State) -> ActionOutput:
        arg_group_idx = len(state.arg_groups or [])
        return NewArgGroupActionOutput(arg_group_idx=arg_group_idx, amount=self.value)

class ArgFromExprAction(ArgFromExprBaseAction):

    def output(self, state: State) -> ArgFromExprActionOutput:
        arg_group_idx = self.arg_group_idx
        arg_idx = self.arg_idx
        expr_id = self.expr_id
        arg_groups = state.arg_groups
        if arg_groups is None:
            raise InvalidActionArgException("No arg groups yet")
        if arg_group_idx < 0 or arg_group_idx >= len(arg_groups):
            raise InvalidActionArgException(f"Invalid arg group index: {arg_group_idx}")
        arg_group = arg_groups[arg_group_idx]
        if arg_idx < 0 or arg_idx >= arg_group.amount:
            raise InvalidActionArgException(f"Invalid arg index: {arg_idx}")
        new_node = state.get_node(expr_id)
        assert new_node is not None, f"Invalid node index: {expr_id}"
        return ArgFromExprActionOutput(
            arg_group_idx=arg_group_idx,
            arg_idx=arg_idx,
            new_node=new_node)

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
        new_node = state.get_node(expr_id)
        if not new_node:
            raise InvalidActionArgException(f"Invalid node index: {expr_id}")
        definition_idx = len(state.definitions or [])
        return NewDefinitionFromExprActionOutput(
            definition_idx=definition_idx,
            new_node=new_node)

class ReplaceByDefinitionAction(DefinitionExprBaseAction):

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

class ExpandDefinitionAction(DefinitionExprBaseAction):

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
