import typing
from utils.types import BaseNode
from .full_state import FullState, NodeTypeHandler, EnvMetaInfo
from .action import Action
from .reward import RewardEvaluator

class Environment:
    def __init__(
        self,
        allowed_node_types: list[NodeTypeHandler[BaseNode, int]],
        allowed_action_types: list[typing.Type[Action]],
        initial_expression: BaseNode,
        max_steps: int = 100000,
        max_history_size: int | None = None,
    ):
        meta = EnvMetaInfo(
            node_types=allowed_node_types,
            action_types=allowed_action_types,
        )
        self.initial_state = FullState(
            meta=meta,
            history=FullState.initial_history(initial_expression),
            max_history_size=max_history_size)
        self.current_state = self.initial_state
        self.reward_evaluator = RewardEvaluator()
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self) -> FullState:
        self.current_state = self.initial_state
        self.current_step = 0
        return self.current_state

    def step(self, action: Action) -> tuple[FullState, float, bool, bool]:
        next_state = self.current_state.apply(action)
        reward = self.reward_evaluator(
            self.current_state.last_state,
            next_state.last_state)
        self.current_step += 1
        terminated = next_state.terminal()
        truncated = self.current_step >= self.max_steps and not terminated
        self.current_state = next_state
        return next_state, reward, terminated, truncated
