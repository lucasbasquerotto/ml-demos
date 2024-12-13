from environment.action import (
    ACTION_ARG_TYPE_PARTIAL_DEFINITION,
    ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
    ACTION_ARG_TYPE_NODE,
    Action,
    ActionInput,
    ActionArgsMetaInfo,
    PartialActionOutput,
    InvalidActionArgException,
)
from environment.state import State, BaseNode

###########################################################
################### BASE IMPLEMENTATION ###################
###########################################################

class PartialDefinitionBaseAction(Action):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        raise NotImplementedError()

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        raise NotImplementedError()

    def __init__(
        self,
        input: ActionInput,
        partial_definition_idx: int,
        node_idx: int,
    ):
        self._input = input
        self._partial_definition_idx = partial_definition_idx
        self._node_idx = node_idx

    @property
    def partial_definition_idx(self) -> int:
        return self._partial_definition_idx

    @property
    def node_idx(self) -> int:
        return self._node_idx

    @property
    def input(self) -> ActionInput:
        return self._input

    def output(self, state: State) -> PartialActionOutput:
        raise NotImplementedError()

    def get_partial_definition_info(
        self,
        state: State,
    ) -> tuple[BaseNode | None, BaseNode | None, int | None]:
        partial_definition_idx = self.partial_definition_idx
        partial_definitions_list = list(state.partial_definitions or [])

        if partial_definition_idx < 0:
            raise InvalidActionArgException(
                f"Invalid partial definition: {partial_definition_idx}")
        if partial_definition_idx >= len(partial_definitions_list):
            raise InvalidActionArgException(
                f"Invalid partial definition: {partial_definition_idx}")

        _, root = partial_definitions_list[partial_definition_idx]

        if self.node_idx == 1:
            return root, None, None

        if root is None:
            raise InvalidActionArgException(
                f"Invalid node index: {self.node_idx}" \
                + f" (empty partial definition: {partial_definition_idx})")

        return state.get_expression_node_info(root=root, node_idx=self.node_idx)

class PartialDefinitionExprBaseAction(PartialDefinitionBaseAction):

    @classmethod
    def metadata(cls) -> ActionArgsMetaInfo:
        return ActionArgsMetaInfo((
            ACTION_ARG_TYPE_PARTIAL_DEFINITION,
            ACTION_ARG_TYPE_NODE,
            ACTION_ARG_TYPE_GLOBAL_EXPRESSION,
        ))

    @classmethod
    def create(cls, input: ActionInput) -> 'Action':
        cls.validate_args_amount(input)
        return cls(
            input=input,
            partial_definition_idx=input.args[0].value,
            node_idx=input.args[1].value,
            expr_id=input.args[2].value,
        )

    def __init__(
        self,
        input: ActionInput,
        partial_definition_idx: int,
        node_idx: int,
        expr_id: int,
    ):
        super().__init__(
            input=input,
            partial_definition_idx=partial_definition_idx,
            node_idx=node_idx,
        )

        self._expr_id = expr_id

    @property
    def expr_id(self) -> int:
        return self._expr_id

    def output(self, state: State) -> PartialActionOutput:
        raise NotImplementedError()

###########################################################
##################### IMPLEMENTATION ######################
###########################################################

class ReplaceNodeAction(PartialDefinitionExprBaseAction):

    def output(self, state: State) -> PartialActionOutput:
        partial_definition_idx = self.partial_definition_idx
        node_idx = self.node_idx
        expr_id = self.expr_id

        new_node = state.get_node(expr_id)
        if new_node is None:
            raise InvalidActionArgException(
                f"Invalid node index: {expr_id}" \
                + f" (partial_definition_idx: {partial_definition_idx})")

        if node_idx == 1:
            return PartialActionOutput(
                partial_definition_idx=partial_definition_idx,
                node_idx=node_idx,
                new_node=new_node)

        node, _, _ = self.get_partial_definition_info(state)

        if node is None:
            raise InvalidActionArgException(
                f"Invalid node index: {node_idx}" \
                + f" (partial_definition_idx: {partial_definition_idx})")

        return PartialActionOutput(
            partial_definition_idx=partial_definition_idx,
            node_idx=node_idx,
            new_node=new_node)
