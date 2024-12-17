import typing
from .state import State, BaseNode, FunctionDefinition
from .action import Action, ActionMetaInfo, ActionInput, ActionOutput
from .reward import RewardEvaluator

T = typing.TypeVar("T", bound=BaseNode)
V = typing.TypeVar("V", bound=int | float)

class ActionData:
    def __init__(self, type: int, input: ActionInput, output: ActionOutput | None):
        self._type = type
        self._input = input
        self._output = output

    @property
    def type(self) -> int:
        return self._type

    @property
    def input(self) -> ActionInput:
        return self._input

    @property
    def output(self) -> ActionOutput | None:
        return self._output

StateHistoryItem = State | ActionData

class NodeValueParams(typing.Generic[T]):
    def __init__(self, node: T, symbols: list[BaseNode], definition_keys: list[FunctionDefinition]):
        self._node = node
        self._symbols = symbols
        self._definition_keys = definition_keys

    @property
    def node(self) -> T:
        return self._node

    @property
    def symbols(self) -> list[BaseNode]:
        return self._symbols

    @property
    def definition_keys(self) -> list[FunctionDefinition]:
        return self._definition_keys

class NodeTypeHandler(typing.Generic[T, V]):
    def __init__(
        self,
        node_type: typing.Type[T],
        get_value: typing.Callable[[NodeValueParams[T]], V],
    ):
        self._node_type = node_type
        self._get_value = get_value

    @property
    def node_type(self) -> typing.Type[T]:
        return self._node_type

    @property
    def get_value(self) -> typing.Callable[[NodeValueParams[T]], V]:
        return self._get_value

class EnvMetaInfo:
    def __init__(
        self,
        main_context: int,
        node_types: tuple[typing.Type[BaseNode], ...],
        atomic_node_handlers: tuple[NodeTypeHandler[BaseNode, int], ...],
        action_types: tuple[typing.Type[Action], ...],
    ):
        self._main_context = main_context
        self._node_types = node_types
        self._atomic_node_handlers = atomic_node_handlers
        self._action_types = action_types
        self._action_types_info = tuple([
            ActionMetaInfo(
                type_idx=i,
                arg_types=action.metadata().arg_types,
            ) for i, action in enumerate(action_types)
        ])

    @property
    def main_context(self) -> int:
        return self._main_context

    @property
    def node_types(self) -> tuple[typing.Type[BaseNode], ...]:
        return self._node_types

    @property
    def atomic_node_handlers(self) -> tuple[NodeTypeHandler[BaseNode, int], ...]:
        return self._atomic_node_handlers

    @property
    def action_types(self) -> tuple[typing.Type[Action], ...]:
        return self._action_types

    @property
    def action_types_info(self) -> tuple[ActionMetaInfo, ...]:
        return self._action_types_info

class FullEnvMetaInfo(EnvMetaInfo):
    def __init__(
        self,
        main_context: int,
        node_types: tuple[typing.Type[BaseNode], ...],
        atomic_node_handlers: tuple[NodeTypeHandler[BaseNode, int], ...],
        action_types: tuple[typing.Type[Action], ...],
        reward_evaluator: RewardEvaluator,
        initial_history: tuple[StateHistoryItem, ...],
        is_terminal: typing.Callable[[State], bool],
    ):
        super().__init__(
            main_context=main_context,
            node_types=node_types,
            atomic_node_handlers=atomic_node_handlers,
            action_types=action_types)
        self._reward_evaluator = reward_evaluator
        self._initial_history = initial_history
        self._is_terminal = is_terminal

    @property
    def reward_evaluator(self) -> RewardEvaluator:
        return self._reward_evaluator

    @property
    def initial_history(self) -> tuple[StateHistoryItem, ...]:
        return self._initial_history

    def is_terminal(self, state: State) -> bool:
        return self._is_terminal(state)
