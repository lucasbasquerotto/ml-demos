import typing
from .state import State, BaseNode, DefinitionKey
from .action import Action, ActionArgType
from .reward import RewardEvaluator

T = typing.TypeVar("T", bound=BaseNode)
V = typing.TypeVar("V", bound=int | float)

class NodeValueParams(typing.Generic[T]):
    def __init__(self, node: T, symbols: list[BaseNode], definition_keys: list[DefinitionKey]):
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
    def definition_keys(self) -> list[DefinitionKey]:
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
        node_types: list[NodeTypeHandler[BaseNode, int]],
        action_types: list[typing.Type[Action]],
    ):
        self._main_context = main_context
        self._node_types = node_types
        self._action_types = action_types
        self._actions_arg_types = [action.metadata().arg_types for action in action_types]

    @property
    def main_context(self) -> int:
        return self._main_context

    @property
    def node_types(self) -> list[NodeTypeHandler[BaseNode, int]]:
        return self._node_types

    @property
    def action_types(self) -> list[typing.Type[Action]]:
        return self._action_types

    @property
    def actions_arg_types(self) -> list[list[ActionArgType]]:
        return self._actions_arg_types

class FullEnvMetaInfo(EnvMetaInfo):
    def __init__(
        self,
        main_context: int,
        node_types: list[NodeTypeHandler[BaseNode, int]],
        action_types: list[typing.Type[Action]],
        is_terminal: typing.Callable[[State], bool],
        reward_evaluator: RewardEvaluator,
    ):
        super().__init__(
            main_context=main_context,
            node_types=node_types,
            action_types=action_types)
        self._reward_evaluator = reward_evaluator
        self._is_terminal = is_terminal

    @property
    def reward_evaluator(self) -> RewardEvaluator:
        return self._reward_evaluator

    def is_terminal(self, state: State) -> bool:
        return self._is_terminal(state)
