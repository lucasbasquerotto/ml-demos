from .state import State

class RewardEvaluator:
    def __call__(self, current_state: State, next_state: State) -> float:
        raise NotImplementedError()

class DefaultRewardEvaluator(RewardEvaluator):
    def __call__(self, current_state: State, next_state: State) -> float:
        if next_state.terminal():
            return 100  # Contradiction reward (end of the episode)
        if next_state == current_state:
            return -10
        # Intermediate reward logic
        return -1  # Small penalty for each step taken