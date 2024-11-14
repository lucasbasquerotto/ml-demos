from .state import State

class Reward:
    def calculate(self, current_state: State, next_state: State, target_state: State) -> int:
        if next_state == target_state:
            return 100  # Goal achievement reward
        if next_state.is_contradictory():
            return 100  # Contradiction reward (end of the episode)
        if next_state == current_state:
            return -10
        # Intermediate reward logic
        return -1  # Small penalty for each step taken
