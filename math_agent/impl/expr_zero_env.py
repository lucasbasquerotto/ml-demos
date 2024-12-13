import typing
from utils.types import BaseNode
from environment.state import State
from environment.action import DEFAULT_ACTIONS
from environment.reward import DefaultRewardEvaluator
from environment.full_state import FullState
from environment.environment import Environment
from environment.meta_env import FullEnvMetaInfo, NodeTypeHandler
from impl import (
    node_types,
    node_handlers,
    reformulation_action_types,
    partial_action_types)

EXPR_ZERO_CONTEXT = 0

class ExprZeroEnv(Environment):
    def __init__(
        self,
        initial_expression: BaseNode,
        max_steps: int = 100000,
        max_history_size: int | None = None,
    ):
        def is_zero(state: State) -> bool | None:
            return state.expression.is_zero

        def is_terminal(state: State) -> bool:
            return is_zero(state) is not None

        atomic_node_handlers = typing.cast(
            tuple[NodeTypeHandler[BaseNode, int], ...],
            (
                node_handlers.definition_handler,
                node_handlers.symbol_handler,
                node_handlers.integer_handler,
            )
        )
        atomic_node_types = [handler.node_type for handler in atomic_node_handlers]

        meta = FullEnvMetaInfo(
            main_context=EXPR_ZERO_CONTEXT,
            node_types=tuple(atomic_node_types + [
                node_types.Add,
            ]),
            atomic_node_handlers=atomic_node_handlers,
            action_types=tuple(DEFAULT_ACTIONS + [
                reformulation_action_types.SimplifyAddAction,
                partial_action_types.ReplaceNodeAction,
            ]),
            reward_evaluator=DefaultRewardEvaluator(is_terminal),
            initial_history=FullState.initial_history(initial_expression),
            is_terminal=is_terminal,
        )

        super().__init__(
            meta=meta,
            max_steps=max_steps,
            max_history_size=max_history_size,
        )

        self._is_zero = is_zero

    def correct(self, state: State) -> bool | None:
        return self._is_zero(state)
