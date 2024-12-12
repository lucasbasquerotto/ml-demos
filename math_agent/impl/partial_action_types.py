from environment.action import (
    ACTION_ARG_TYPE_PARTIAL_DEFINITION,
    ACTION_ARG_TYPE_NODE,
    Action,
    ActionInput,
    ActionOutput,
    ActionArgsMetaInfo,
)
from environment.state import State

###########################################################
################### BASE IMPLEMENTATION ###################
###########################################################

class PartialDefinitionNodeChangeBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo([
            ACTION_ARG_TYPE_PARTIAL_DEFINITION,
            ACTION_ARG_TYPE_NODE,
        ])

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            partial_definition_idx=input.args[0].value,
            node_idx=input.args[1].value,
        )

    def __init__(self, input: ActionInput, partial_definition_idx: int, node_idx: int):
        self._input = input
        self._partial_definition_idx = partial_definition_idx
        self._node_idx = node_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def expr_id(self) -> int:
        return self._node_idx

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> ActionOutput:
        raise NotImplementedError()

###########################################################
##################### IMPLEMENTATION ######################
###########################################################
