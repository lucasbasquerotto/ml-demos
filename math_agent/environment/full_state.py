import numpy as np
from .state import State, BaseNode, DefinitionKey
from .action import Action, ActionInput, ActionOutput
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

ACTION_OUTPUT_SUBCONTEXT_NODE_IDX = 0
ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR = 1
ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR = 1

# context index (e.g: main expression, definition expressions, assumptions)
# subcontext index (e.g: which definition, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, definition, integer, function/operator)
# node value (e.g: symbol index, definition index, integer value, function/operator index)

class ActionData:
    def __init__(self, type: int, input: ActionInput, output: ActionOutput):
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
    def output(self) -> ActionOutput:
        return self._output

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
        action_type = action_types.index(type(action))
        assert action_type >= 0, f"Action type not found: {type(action)}"

        action_input = action.input()
        action_output = action.output(last_state)

        next_state = last_state.apply(action_output)

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

    def to_raw_state(self) -> np.ndarray[np.int_, np.dtype]:
        meta_state = self._raw_meta_state(history_number=0)
        main_states = np.array([], dtype=np.int_)
        action_states = np.array([], dtype=np.int_)

        for i, history in enumerate(self._history):
            if isinstance(history, State):
                main_state = self._raw_main_state(history_number=i+1, state=history)
                main_states = np.concatenate([main_states, [main_state]])
            elif isinstance(history, ActionData):
                action_state = self._raw_action_state(history_number=i+1, action_data=history)
                action_states = np.concatenate([action_states, [action_state]])

        state = np.concatenate([
            [meta_state],
            main_states,
            action_states,
        ])

        return state

    def _raw_meta_state(self, history_number: int) -> np.ndarray[np.int_, np.dtype]:
        meta = self._meta

        action_amount_nodes = []
        action_arg_nodes = []

        for i, arg_types in enumerate(meta.actions_arg_types):
            action_amount_nodes.append(
                self._named_node_state_item(
                    history_number=history_number,
                    history_type=HISTORY_TYPE_META,
                    context=META_ACTION_AMOUNT_CONTEXT,
                    subcontext=i,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=0,
                    node_value=len(arg_types),
                )
            )

            for j, arg_type in enumerate(arg_types):
                action_arg_nodes.append(
                    self._named_node_state_item(
                        history_number=history_number,
                        history_type=HISTORY_TYPE_META,
                        context=META_ACTION_ARG_CONTEXT,
                        subcontext=i,
                        parent_node_idx=0,
                        node_idx=j+1,
                        atomic_node=1,
                        node_type=arg_type,
                        node_value=0,
                    )
                )

        nodes: np.ndarray[np.int_, np.dtype] = np.concatenate([
            action_amount_nodes,
            action_arg_nodes,
        ])

        return nodes

    def _raw_main_state(self, history_number: int, state: State) -> np.ndarray[np.int_, np.dtype]:
        definition_keys = [d for d, _ in state.definitions or []]
        symbols = list(state.expression.free_symbols or set())

        main_state_nodes, _ = self._to_node_state_array(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_MAIN_CONTEXT,
            subcontext=0,
            parent_node_idx=0,
            node_idx=1,
            node=state.expression,
            symbols=symbols,
            definition_keys=definition_keys,
        )

        definitions_nodes = self._to_context_items_array(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_DEFINITION_CONTEXT,
            expressions=[expr for _, expr in state.definitions or []],
            symbols=symbols,
            definition_keys=definition_keys,
        )

        assumptions_nodes = self._to_context_items_array(
            history_number=history_number,
            history_type=HISTORY_TYPE_STATE,
            context=STATE_ASSUMPTION_CONTEXT,
            expressions=list(state.assumptions or []),
            symbols=symbols,
            definition_keys=definition_keys,
        )

        nodes: np.ndarray[np.int_, np.dtype] = np.concatenate([
            main_state_nodes,
            definitions_nodes,
            assumptions_nodes,
        ])

        return nodes

    def _raw_action_state(
        self,
        history_number: int,
        action_data: ActionData,
    ) -> np.ndarray[np.int_, np.dtype]:
        action_input = action_data.input
        action_output = action_data.output

        action_node = self._named_node_state_item(
            history_number=history_number,
            history_type=HISTORY_TYPE_ACTION,
            context=ACTION_TYPE_CONTEXT,
            subcontext=0,
            parent_node_idx=0,
            node_idx=1,
            atomic_node=1,
            node_type=action_data.type,
            node_value=0,
        )

        action_arg_nodes = []

        for i, arg in enumerate(action_input.args):
            arg_node = self._named_node_state_item(
                history_number=history_number,
                history_type=HISTORY_TYPE_ACTION,
                context=ACTION_INPUT_CONTEXT,
                subcontext=i+1,
                parent_node_idx=0,
                node_idx=1,
                atomic_node=1,
                node_type=arg.type,
                node_value=arg.value,
            )
            action_arg_nodes.append(arg_node)

        output_idx_node = self._named_node_state_item(
            history_number=history_number,
            history_type=HISTORY_TYPE_ACTION,
            context=ACTION_OUTPUT_CONTEXT,
            subcontext=ACTION_OUTPUT_SUBCONTEXT_NODE_IDX,
            parent_node_idx=0,
            node_idx=1,
            atomic_node=1,
            node_type=0,
            node_value=action_output.node_idx,
        )

        output_expr_nodes, _ = self._to_node_state_array(
            history_number=history_number,
            history_type=HISTORY_TYPE_ACTION,
            context=ACTION_OUTPUT_CONTEXT,
            subcontext=ACTION_OUTPUT_SUBCONTEXT_NODE_EXPR,
            parent_node_idx=0,
            node_idx=1,
            node=action_output.new_node,
            symbols=[],
            definition_keys=[],
        )

        nodes: np.ndarray[np.int_, np.dtype] = np.concatenate([
            [action_node],
            action_arg_nodes,
            [output_idx_node],
            output_expr_nodes,
        ])

        return nodes


    def _to_context_items_array(
        self,
        history_number: int,
        history_type: int,
        context: int,
        expressions: list[BaseNode],
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> np.ndarray[np.int_, np.dtype]:
        nodes: np.ndarray[np.int_, np.dtype] = np.array([], dtype=np.int_)

        for i, node in enumerate(expressions):
            context = STATE_DEFINITION_CONTEXT
            subcontext = i
            parent_node_idx = 0
            node_idx = parent_node_idx + 1

            iter_nodes, node_idx = self._to_node_state_array(
                history_number=history_number,
                history_type=history_type,
                context=context,
                subcontext=subcontext,
                parent_node_idx=parent_node_idx,
                node_idx=node_idx,
                node=node,
                symbols=symbols,
                definition_keys=definition_keys,
            )

            nodes = np.concatenate([
                nodes,
                iter_nodes,
            ])

        return nodes

    def _to_node_state_array(
        self,
        history_number: int,
        history_type: int,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: BaseNode,
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> tuple[np.ndarray[np.int_, np.dtype], int]:
        state_array = np.array(self._to_leaf_state(
            history_number=history_number,
            history_type=history_type,
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            node=node,
            symbols=symbols,
            definition_keys=definition_keys,
        ))

        next_node_idx = node_idx + 1

        for arg in node.args:
            inner_node_array, next_node_idx = self._to_node_state_array(
            history_number=history_number,
            history_type=history_type,
                context=context,
                subcontext=subcontext,
                parent_node_idx=node_idx,
                node_idx=next_node_idx,
                node=arg,
                symbols=symbols,
                definition_keys=definition_keys,
            )

            state_array = np.concatenate([
                state_array,
                inner_node_array,
            ])

        return state_array, next_node_idx

    def _to_leaf_state(
        self,
        history_number: int,
        history_type: int,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: BaseNode,
        symbols: list[BaseNode],
        definition_keys: list[DefinitionKey],
    ) -> list[int]:
        meta = self._meta
        handler = next(h for h in meta.node_types if isinstance(node, h.node_type))
        assert handler is not None, f"Handler not found for node: {node}"
        atomic_node = len(node.args) == 0
        node_type = meta.node_types.index(handler)
        node_value = handler.get_value(NodeValueParams(
            node=node,
            symbols=symbols,
            definition_keys=definition_keys,
        ))
        result = self._named_node_state_item(
            history_number=history_number,
            history_type=history_type,
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            atomic_node=atomic_node,
            node_type=node_type,
            node_value=node_value,
        )
        return result

    def _named_node_state_item(
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
    ) -> list[int]:
        return [
            history_number,
            history_type,
            context,
            subcontext,
            parent_node_idx,
            node_idx,
            atomic_node,
            node_type,
            node_value,
        ]
