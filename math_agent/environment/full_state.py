import numpy as np
from utils.types import ActionOutput, ReformulationActionOutput, NewPartialDefinitionActionOutput
from utils.logger import logger
from .state import State, BaseNode, DefinitionKey
from .action import Action, ActionInput, InvalidActionException
from .meta_env import NodeValueParams, EnvMetaInfo

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
ACTION_OUTPUT_SUBCONTEXT_NODE_IDX = 3
ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR = 4

ACTION_STATUS_SKIP_ID = 0
ACTION_STATUS_SUCCESS_ID = 1
ACTION_STATUS_FAIL_ID = 2

UNKNOWN_OR_EMPTY_NODE_TYPE = 0

# context index (e.g: main expression, definition expressions, assumptions)
# subcontext index (e.g: which definition, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, definition, integer, function/operator)
# node value (e.g: symbol index, definition index, integer value, function/operator index)

class ActionData:
    def __init__(self, type: int, input: ActionInput, output: ActionOutput | None):
        self._type = type
        self._input = input
        self._output = output

    @property
    def type(self) -> int:
        return self._type

    @property
    def input(self) -> ActionInput:
        return self._input

    @property
    def output(self) -> ActionOutput | None:
        return self._output

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
        history: list[State | ActionData],
        max_history_size: int | None = None,
    ):
        assert len(meta.node_types) > 0, "No node types"
        assert len(meta.node_types) == len(set(meta.node_types)), "Duplicate node types"
        assert len(meta.action_types) > 0, "No action types"
        assert len(meta.action_types) == len(set(meta.action_types)), "Duplicate action types"
        self._meta = meta
        self._history = history
        self._max_history_size = max_history_size

    @classmethod
    def initial_history(cls, expression: BaseNode) -> list[State | ActionData]:
        return [State(expression)]

    @property
    def last_state(self) -> State:
        for i in range(len(self._history) - 1, -1, -1):
            item = self._history[i]
            if isinstance(item, State):
                return item

        raise ValueError("No state found in history")

    def _is_zero(self) -> bool | None:
        last_state = self._history[-1]
        assert isinstance(last_state, State)
        return last_state.expression.is_zero

    def terminal(self) -> bool:
        return self._is_zero() is not None

    def correct(self) -> bool | None:
        return self._is_zero()

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
            action_output = action.output(last_state)
            next_state = last_state.apply(action_output)
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
                nodes_state = self._node_data_list_state(history_number=i+1, state=history_item)
                nodes_states += nodes_state
            elif isinstance(history_item, ActionData):
                nodes_action = self._node_data_list_action(history_number=i+1, action_data=history_item)
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

        action_node = NodeItemData(
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

        action_arg_nodes: list[NodeItemData] = []

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
            action_arg_nodes.append(arg_node)

        nodes: list[NodeItemData] = [action_node] + action_arg_nodes

        if action_output is not None:
            if isinstance(action_output, ReformulationActionOutput):
                output_idx_node = NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_NODE_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=UNKNOWN_OR_EMPTY_NODE_TYPE,
                    node_value=action_output.expr_id,
                    history_expr_id=None,
                    node=None,
                )

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

                nodes += [output_idx_node] + output_expr_nodes
            elif isinstance(action_output, NewPartialDefinitionActionOutput):
                output_idx_node = NodeItemData(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_ACTION,
                    context=ACTION_OUTPUT_CONTEXT,
                    subcontext=ACTION_OUTPUT_SUBCONTEXT_PARTIAL_DEFINITION_IDX,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=UNKNOWN_OR_EMPTY_NODE_TYPE,
                    node_value=action_output.partial_definition_idx,
                    history_expr_id=None,
                    node=None,
                )

                nodes += [output_idx_node]

                if action_output.expr_id is not None:
                    output_idx_node = NodeItemData(
                        history_number=history_number,
                        history_type=HISTORY_TYPE_ACTION,
                        context=ACTION_OUTPUT_CONTEXT,
                        subcontext=ACTION_OUTPUT_SUBCONTEXT_NODE_IDX,
                        parent_node_idx=0,
                        node_idx=1,
                        atomic_node=1,
                        node_type=UNKNOWN_OR_EMPTY_NODE_TYPE,
                        node_value=action_output.expr_id,
                        history_expr_id=None,
                        node=None,
                    )

                    nodes += [output_idx_node]
            else:
                raise NotImplementedError(f"Action output not implemented: {type(action_output)}")

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
            handler = next(h for h in meta.node_types if isinstance(node, h.node_type))
            assert handler is not None, f"Handler not found for node: {node}"
            atomic_node = int(len(node.args) == 0)
            # node_type = 0 is for special node types (e.g: unknown, empty)
            node_type = meta.node_types.index(handler) + 1
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
