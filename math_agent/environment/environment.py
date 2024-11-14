from .state import State
from .action import Action
from .transition import Transition
from .reward import Reward

class Environment:
    def __init__(self, initial_expression: str, target_expression: str, max_steps: int = 100):
        self.initial_state = State(initial_expression)
        self.target_state = State(target_expression)
        self.current_state = self.initial_state
        self.transition = Transition()
        self.reward = Reward()
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self) -> State:
        self.current_state = self.initial_state
        self.current_step = 0
        return self.current_state

    def step(self, action: Action) -> tuple[State, int, bool, bool]:
        next_state = self.transition.apply(self.current_state, action)
        reward = self.reward.calculate(self.current_state, next_state, self.target_state)
        self.current_step += 1
        terminated = next_state == self.target_state or next_state.is_contradictory()
        truncated = self.current_step >= self.max_steps and not terminated
        self.current_state = next_state
        return next_state, reward, terminated, truncated
