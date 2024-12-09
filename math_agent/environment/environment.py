import typing
from utils.types import BaseNode
from .state import State, NodeTypeHandler
from .action import Action
from .reward import RewardEvaluator

class Environment:
    def __init__(
        self,
        allowed_node_types: list[NodeTypeHandler[BaseNode, int]],
        allowed_action_types: list[typing.Type[Action]],
        initial_expression: BaseNode,
        max_steps: int = 100000,
    ):
        self.initial_state = State(
            node_types=allowed_node_types,
            action_types_args=[action.metadata() for action in allowed_action_types],
            expression=initial_expression)
        self.current_state = self.initial_state
        self.reward_evaluator = RewardEvaluator()
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self) -> State:
        self.current_state = self.initial_state
        self.current_step = 0
        return self.current_state

    def step(self, action: Action) -> tuple[State, float, bool, bool]:
        next_state = action.apply(self.current_state)
        reward = self.reward_evaluator(self.current_state, next_state)
        self.current_step += 1
        terminated = next_state.terminal()
        truncated = self.current_step >= self.max_steps and not terminated
        self.current_state = next_state
        return next_state, reward, terminated, truncated
