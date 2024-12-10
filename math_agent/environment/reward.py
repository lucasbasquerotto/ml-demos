import typing
from .state import State

class RewardEvaluator:
    def __call__(self, current_state: State, next_state: State) -> float:
        raise NotImplementedError()

class DefaultRewardEvaluator(RewardEvaluator):
    def __init__(self, is_terminal: typing.Callable[[State], bool]):
        self._is_terminal = is_terminal

    def __call__(self, current_state: State, next_state: State) -> float:
        if self._is_terminal(next_state):
            return 100  # Reached the objective
        if next_state == current_state:
            return -10 # No change applied
        return -1  # Small penalty for each step taken
