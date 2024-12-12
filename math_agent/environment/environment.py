from .full_state import FullState, Action
from .meta_env import FullEnvMetaInfo

class Environment:
    def __init__(
        self,
        meta: FullEnvMetaInfo,
        max_steps: int = 100000,
        max_history_size: int | None = None,
    ):
        self._meta = meta
        self._initial_state = FullState(
            meta=meta,
            history=meta.initial_history,
            max_history_size=max_history_size)
        self._current_state = self._initial_state
        self._max_steps = max_steps
        self._current_step = 0

    def reset(self) -> FullState:
        self._current_state = self._initial_state
        self._current_step = 0
        return self._current_state

    def step(self, action: Action) -> tuple[FullState, float, bool, bool]:
        meta = self._meta
        reward_evaluator = meta.reward_evaluator
        next_state = self._current_state.apply(action)
        reward = reward_evaluator(
            self._current_state.last_state,
            next_state.last_state)
        self._current_step += 1
        last_state = next_state.last_state
        assert last_state is not None
        terminated = meta.is_terminal(last_state)
        truncated = self._current_step >= self._max_steps and not terminated
        self._current_state = next_state
        return next_state, reward, terminated, truncated
