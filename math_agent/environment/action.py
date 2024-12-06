from utils.types import ActionArgsMetaInfo
from .state import State

class Action:
    @classmethod
    def from_raw_action(cls, action: tuple[int, ...]) -> 'Action':
        raise NotImplementedError()

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        raise NotImplementedError()

    def apply(self, state: State) -> State:
        raise NotImplementedError()
