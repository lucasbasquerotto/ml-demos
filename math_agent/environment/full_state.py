import numpy as np
from utils.logger import logger
from .state import State, BaseNode, DefinitionKey
from .action import (
    Action,
    InvalidActionException,
    ActionOutput,
    NewPartialDefinitionActionOutput,
    NewDefinitionFromPartialActionOutput,
    NewDefinitionFromNodeActionOutput,
    ReplaceByDefinitionActionOutput,
    ExpandDefinitionActionOutput,
    ReformulationActionOutput,
    PartialActionOutput)
from .meta_env import NodeValueParams, EnvMetaInfo, ActionData, StateHistoryItem

HISTORY_TYPE_META = 0
HISTORY_TYPE_STATE = 1
HISTORY_TYPE_ACTION = 2

META_MAIN_CONTEXT = 0
META_ACTION_AMOUNT_CONTEXT = 1
META_ACTION_ARG_CONTEXT = 2

STATE_MAIN_CONTEXT = 0
STATE_DEFINITION_CONTEXT = 1
STATE_ASSUMPTION_CONTEXT = 2

ACTION_TYPE_CONTEXT = 0
ACTION_INPUT_CONTEXT = 1
ACTION_OUTPUT_CONTEXT = 2
ACTION_STATUS_CONTEXT = 3

ACTION_OUTPUT_SUBCONTEXT_PARTIAL_DEFINITION_IDX = 1
ACTION_OUTPUT_SUBCONTEXT_DEFINITION_IDX = 2
ACTION_OUTPUT_SUBCONTEXT_EXPR_ID = 3
ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR = 4

ACTION_STATUS_SKIP_ID = 0
ACTION_STATUS_SUCCESS_ID = 1
ACTION_STATUS_FAIL_ID = 2

UNKNOWN_OR_EMPTY_NODE_TYPE = 0

action_output_types = [
    NewPartialDefinitionActionOutput,
    NewDefinitionFromPartialActionOutput,
    NewDefinitionFromNodeActionOutput,
    ReplaceByDefinitionActionOutput,
    ExpandDefinitionActionOutput,
    ReformulationActionOutput,
    PartialActionOutput,
]

# context index (e.g: main expression, definition expressions, assumptions)
# subcontext index (e.g: which definition, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, definition, integer, function/operator)
# node value (e.g: symbol index, definition index, integer value, function/operator index)

class NodeItemData:
    def __init__(
        self,
        history_number: int,
        history_type: int,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        atomic_node: int,
        node_type: int,
        node_value: int,
        history_expr_id: int | None,
        node: BaseNode | None,
    ):
        if history_expr_id is not None:
            assert history_expr_id > 0, f"Invalid history expression id: {history_expr_id}"

        self._history_number = history_number
        self._history_type = history_type
        self._context = context
        self._subcontext = subcontext
        self._parent_node_idx = parent_node_idx
        self._node_idx = node_idx
        self._atomic_node = atomic_node
        self._node_type = node_type
        self._node_value = node_value
        self._history_expr_id = history_expr_id
        self._node = node

    @property
    def history_number(self) -> int:
        return self._history_number

    @property
    def history_type(self) -> int:
        return self._history_type

    @property
    def context(self) -> int:
        return self._context

    @property
    def subcontext(self) -> int:
        return self._subcontext

    @property
    def parent_node_idx(self) -> int:
        return self._parent_node_idx

    @property
    def node_idx(self) -> int:
        return self._node_idx

    @property
    def atomic_node(self) -> int:
        return self._atomic_node

    @property
    def node_type(self) -> int:
        return self._node_type

    @property
    def node_value(self) -> int:
        return self._node_value

    @property
    def history_expr_id(self) -> int | None:
        return self._history_expr_id

    @property
    def node(self) -> BaseNode | None:
        return self.node

    def to_array(self) -> np.ndarray[np.int_, np.dtype]:
        return np.array([
            self._history_number,
            self._history_type,
            self._context,
            self._subcontext,
            self._parent_node_idx,
            self._node_idx,
            self._atomic_node,
            self._node_type,
            self._node_value,
            self._history_expr_id or 0,
        ])

class FullState:
    def __init__(
        self,
        meta: EnvMetaInfo,
        history: list[StateHistoryItem],
        max_history_size: int | None = None,
    ):
        assert len(meta.node_handlers) > 0, "No node types"
        assert len(meta.node_handlers) == len(set(meta.node_handlers)), "Duplicate node types"
        assert len(meta.action_types) > 0, "No action types"
        assert len(meta.action_types) == len(set(meta.action_types)), "Duplicate action types"
        self._meta = meta
        self._history = history
        self._max_history_size = max_history_size

    @classmethod
    def initial_history(cls, expression: BaseNode) -> list[StateHistoryItem]:
        return [State(expression)]

    @property
    def last_state(self) -> State:
        for i in range(len(self._history) - 1, -1, -1):
            item = self._history[i]
            if isinstance(item, State):
                return item

        raise ValueError("No state found in history")

    def apply(self, action: Action) -> 'FullState':
        last_state = self._history[-1]
        assert isinstance(last_state, State)

        action_types = self._meta.action_types
        # action type index (0 is for no action)
        action_type = action_types.index(type(action)) + 1
        assert action_type >= 1, f"Action type not found: {type(action)}"

        action_input = action.input
        action_output: ActionOutput | None

        try:
            next_state = action.apply(last_state)
        except InvalidActionException as e:
            logger.debug(f"Invalid action: {e}")
            action_type = 0
            action_output = None
            next_state = last_state

        action_data = ActionData(
            type=action_type,
            input=action_input,
            output=action_output,
        )

        history = self._history.copy()
        history.append(action_data)
        history.append(next_state)

        if self._max_history_size is not None:
            history = history[-self._max_history_size:]

        return FullState(
            meta=self._meta,
            history=history,
            max_history_size=self._max_history_size,
        )

    def raw_data(self) -> np.ndarray[np.int_, np.dtype]:
        nodes = self.node_data_list()
        data = np.array([node.to_array() for node in nodes])
        return data

    def node_data_list(self) -> list[NodeItemData]:
        nodes_meta = self._node_data_list_meta(history_number=0)
        nodes_states: list[NodeItemData] = []
        nodes_actions: list[NodeItemData] = []

        for i, history_item in enumerate(self._history):
            if isinstance(history_item, State):
                nodes_state = self._node_data_list_state(
                    history_number=i+1,
                    state=history_item)
                nodes_states += nodes_state
            elif isinstance(history_item, ActionData):
                nodes_action = self._node_data_list_action(
                    history_number=i+1,
                    action_data=history_item)
                nodes_actions += nodes_action

        nodes = nodes_meta + nodes_states + nodes_actions

        return nodes

    def _node_data_list_meta(self, history_number: int) -> list[NodeItemData]:
        meta = self._meta
        nodes: list[NodeItemData] = []

        for i, arg_types in enumerate(meta.actions_arg_types):
            nodes.append(NodeItemData(
                history_number=history_number,
                history_type=HISTORY_TYPE_META,
                context=META_ACTION_AMOUNT_CONTEXT,
                subcontext=i,
                parent_node_idx=0,
                node_idx=1,
                atomic_node=1,
                node_type=UNKNOWN_OR_EMPTY_NODE_TYPE,
                node_value=len(arg_types),
                history_expr_id=None,
                node=None,
            ))

            for j, arg_type in enumerate(arg_types):
                nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_META,
                    context=META_ACTION_ARG_CONTEXT,
                    subcontext=i,
                    parent_node_idx=0,
                    node_idx=j+1,
                    atomic_node=1,
                    node_type=arg_type,
                    node_value=0,
                    history_expr_id=None,
                    node=None,
                ))

        return nodes

    def _node_data_list_state(self, history_number: int, state: State) -> list[NodeItemData]:
        definition_keys = [d for d, _ in state.definitions or []]
        symbols = list(state.expression.free_symbols or set())
        history_expr_id = 1

        main_state_nodes, _, history_expr_id = self._node_tree_data_list(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_MAIN_CONTEXT,
            subcontext=0,
            parent_node_idx=0,
            node_idx=1,
            history_expr_id=history_expr_id,
            node=state.expression,
            symbols=symbols,
            definition_keys=definition_keys,
        )

        definitions_nodes, history_expr_id = self._context_node_data_list(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_DEFINITION_CONTEXT,
            expressions=[expr for _, expr in state.definitions or []],
            history_expr_id=history_expr_id,
            symbols=symbols,
            definition_keys=definition_keys,
        )

        assumptions_nodes, history_expr_id = self._context_node_data_list(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_ASSUMPTION_CONTEXT,
            expressions=list(state.assumptions or []),
            history_expr_id=history_expr_id,
            symbols=symbols,
            definition_keys=definition_keys,
        )

        nodes: list[NodeItemData] = main_state_nodes + definitions_nodes + assumptions_nodes

        return nodes

    def _node_data_list_action(
        self,
        history_number: int,
        action_data: ActionData,
    ) -> list[NodeItemData]:
        action_input = action_data.input
        action_output = action_data.output
        history_expr_id = 1

        action_type_node = NodeItemData(
            history_number=history_number,
            history_type=HISTORY_TYPE_ACTION,
            context=ACTION_TYPE_CONTEXT,
            subcontext=0,
            parent_node_idx=0,
            node_idx=1,
            atomic_node=1,
            node_type=action_data.type,
            node_value=0,
            history_expr_id=None,
            node=None,
        )

        action_input_nodes: list[NodeItemData] = []

        for i, arg in enumerate(action_input.args):
            arg_node = NodeItemData(
                history_number=history_number,
                history_type=HISTORY_TYPE_ACTION,
                context=ACTION_INPUT_CONTEXT,
                subcontext=i+1,
                parent_node_idx=0,
                node_idx=1,
                atomic_node=1,
                node_type=arg.type,
                node_value=arg.value,
                history_expr_id=None,
                node=None,
            )
            action_input_nodes.append(arg_node)

        action_output_nodes: list[NodeItemData] = []

        if action_output is not None:
            action_output_type = action_output_types.index(type(action_output)) + 1
            assert action_output_type >= 1, f"Action output type not found: {type(action_output)}"

            if isinstance(action_output, NewPartialDefinitionActionOutput):
                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_PARTIAL_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.partial_definition_idx,
                    history_expr_id=None,
                    node=None,
                ))
            elif isinstance(action_output, NewDefinitionFromPartialActionOutput):
                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.definition_idx,
                    history_expr_id=None,
                    node=None,
                ))

                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_PARTIAL_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.partial_definition_idx,
                    history_expr_id=None,
                    node=None,
                ))
            elif isinstance(action_output, NewDefinitionFromNodeActionOutput):
                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.definition_idx,
                    history_expr_id=None,
                    node=None,
                ))

                if action_output.expr_id is not None:
                    action_output_nodes.append(NodeItemData(
                        history_number=history_number,
                        history_type=HISTORY_TYPE_ACTION,
                        context=ACTION_OUTPUT_CONTEXT,
                        subcontext=ACTION_OUTPUT_SUBCONTEXT_EXPR_ID,
                        parent_node_idx=0,
                        node_idx=1,
                        atomic_node=1,
                        node_type=action_output_type,
                        node_value=action_output.expr_id,
                        history_expr_id=None,
                        node=None,
                    ))
            elif isinstance(action_output, ReplaceByDefinitionActionOutput):
                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.definition_idx,
                    history_expr_id=None,
                    node=None,
                ))

                if action_output.expr_id is not None:
                    action_output_nodes.append(NodeItemData(
                        history_number=history_number,
                        history_type=HISTORY_TYPE_ACTION,
                        context=ACTION_OUTPUT_CONTEXT,
                        subcontext=ACTION_OUTPUT_SUBCONTEXT_EXPR_ID,
                        parent_node_idx=0,
                        node_idx=1,
                        atomic_node=1,
                        node_type=action_output_type,
                        node_value=action_output.expr_id,
                        history_expr_id=None,
                        node=None,
                    ))
            elif isinstance(action_output, ReformulationActionOutput):
                action_output_nodes.append(NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_EXPR_ID,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=action_output_type,
                    node_value=action_output.expr_id,
                    history_expr_id=None,
                    node=None,
                ))

                output_expr_nodes, _, history_expr_id = self._node_tree_data_list(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR,
                    parent_node_idx=0,
                    node_idx=1,
                    history_expr_id=history_expr_id,
                    node=action_output.new_node,
                    symbols=[],
                    definition_keys=[],
                )
                action_output_nodes += output_expr_nodes
            else:
                raise NotImplementedError(f"Action output not implemented: {type(action_output)}")


        nodes: list[NodeItemData] = [action_type_node] + action_input_nodes + action_output_nodes

        return nodes

    def _context_node_data_list(
        self,
        history_number: int,
        history_type: int,
        context: int,
        expressions: list[BaseNode | None],
        history_expr_id: int,
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> tuple[list[NodeItemData], int]:
        nodes: list[NodeItemData] = []

        for i, node in enumerate(expressions):
            context = STATE_DEFINITION_CONTEXT
            subcontext = i
            parent_node_idx = 0
            node_idx = parent_node_idx + 1

            iter_nodes, node_idx, history_expr_id = self._node_tree_data_list(
                history_number=history_number,
                history_type=history_type,
                context=context,
                subcontext=subcontext,
                parent_node_idx=parent_node_idx,
                node_idx=node_idx,
                history_expr_id=history_expr_id,
                node=node,
                symbols=symbols,
                definition_keys=definition_keys,
            )

            nodes += iter_nodes

        return nodes, history_expr_id

    def _node_tree_data_list(
        self,
        history_number: int,
        history_type: int,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        history_expr_id: int,
        node: BaseNode | None,
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> tuple[list[NodeItemData], int, int]:
        node_data = self._leaf_node_data(
            history_number=history_number,
            history_type=history_type,
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            history_expr_id=history_expr_id,
            node=node,
            symbols=symbols,
            definition_keys=definition_keys,
        )
        nodes: list[NodeItemData] = [node_data]

        next_node_idx = node_idx + 1
        next_history_expr_id = history_expr_id + 1

        if node is None:
            return nodes, next_node_idx, next_history_expr_id

        for arg in node.args:
            inner_nodes, next_node_idx, next_history_expr_id = self._node_tree_data_list(
                history_number=history_number,
                history_type=history_type,
                context=context,
                subcontext=subcontext,
                parent_node_idx=node_idx,
                node_idx=next_node_idx,
                history_expr_id=next_history_expr_id,
                node=arg,
                symbols=symbols,
                definition_keys=definition_keys,
            )

            nodes += inner_nodes

        return nodes, next_node_idx, next_history_expr_id

    def _leaf_node_data(
        self,
        history_number: int,
        history_type: int,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        history_expr_id: int | None,
        node: BaseNode | None,
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> NodeItemData:
        meta = self._meta

        if node is not None:
            handler_idx, handler = next(
                (i, h)
                for i, h in enumerate(meta.node_handlers)
                if isinstance(node, h.node_type))
            assert handler is not None, f"Handler not found for node: {node}"
            atomic_node = int(len(node.args) == 0)
            # node_type = 0 is for special node types (e.g: unknown, empty)
            node_type = handler_idx + 1
            node_value = handler.get_value(NodeValueParams(
                node=node,
                symbols=symbols,
                definition_keys=definition_keys,
            ))
        else:
            atomic_node = 1
            node_type = UNKNOWN_OR_EMPTY_NODE_TYPE
            node_value = 0

        result = NodeItemData(
            history_number=history_number,
            history_type=history_type,
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            atomic_node=atomic_node,
            node_type=node_type,
            node_value=node_value,
            history_expr_id=history_expr_id,
            node=node,
        )

        return result
