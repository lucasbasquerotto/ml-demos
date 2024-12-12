from utils.types import BaseNode
from environment.state import State
from environment.action import DEFAULT_ACTIONS
from environment.reward import DefaultRewardEvaluator
from environment.full_state import FullState
from environment.environment import Environment
from environment.meta_env import FullEnvMetaInfo
from impl.node_handlers import (
    definition_handler,
    symbol_handler,
    integer_handler
)
from impl.reformulation_action_types import (
    SimplifyAddAction
)

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

        meta = FullEnvMetaInfo(
            main_context=EXPR_ZERO_CONTEXT,
            node_handlers=[
                definition_handler,
                symbol_handler,
                integer_handler,
            ],
            action_types=DEFAULT_ACTIONS + [
                SimplifyAddAction,
            ],
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