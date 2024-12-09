import typing
import numpy as np
from utils.types import BaseNode, DefinitionKey, Assumption, ActionArgsMetaInfo

MAIN_CONTEXT = 0
DEFINITION_CONTEXT = 1
ASSUMPTION_CONTEXT = 2
ACTION_AMOUNT_CONTEXT = 3
ACTION_ARGS_CONTEXT = 4

T = typing.TypeVar("T", bound=BaseNode)
V = typing.TypeVar("V", bound=int | float)

# context index (e.g: main expression, definition expressions, assumptions)
# subcontext index (e.g: which definition, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, definition, integer, function/operator)
# node value (e.g: symbol index, definition index, integer value, function/operator index)

class NodeValueParams(typing.Generic[T]):
    def __init__(self, node: T, symbols: list[BaseNode], definition_keys: list[DefinitionKey]):
        self.node = node
        self.symbols = symbols
        self.definition_keys = definition_keys

class NodeTypeHandler(typing.Generic[T, V]):
    def __init__(
        self,
        node_type: typing.Type[T],
        get_value: typing.Callable[[NodeValueParams[T]], V],
    ):
        self.node_type = node_type
        self.get_value = get_value

class State:
    def __init__(
        self,
        node_types: list[NodeTypeHandler[BaseNode, int]],
        action_types_args: list[ActionArgsMetaInfo],
        expression: BaseNode,
        definitions: list[tuple[DefinitionKey, BaseNode]] | None = None,
        assumptions: list[Assumption] | None = None,
    ):
        definition_keys = [d for d, _ in definitions] if definitions else []
        assumption_keys = assumptions or []

        self._node_types = node_types
        self._action_types_args = action_types_args
        self._expression = expression
        self._definitions = definitions
        self._definition_keys = definition_keys
        self._definition_key_set = set(definition_keys)
        self._assumptions = assumptions
        self._assumption_keys = assumption_keys
        self._symbols = list(expression.free_symbols or set())

    @classmethod
    def index_to_node(cls, root: BaseNode, index: int) -> BaseNode | None:
        node, _ = cls._index_to_node(root, index)
        return node

    @classmethod
    def _index_to_node(cls, root: BaseNode, index: int) -> tuple[BaseNode | None, int]:
        assert index > 0, f"Invalid index for root node: {index}"
        assert isinstance(index, int), f"Invalid index type for root node: {type(index)} ({index})"
        index -= 1
        node: BaseNode | None = root

        if index > 0:
            for arg in root.args:
                # recursive call each node arg to traverse its subtree
                node, index = cls._index_to_node(root=arg, index=index)
                assert index >= 0, f"Invalid index for node: {index}"
                # it will end when index = 0 (it's the actual node, if any)
                # otherwise, it will go to the next arg
                if index == 0:
                    break

        return node if (index == 0) else None, index


    def terminal(self) -> bool:
        return self._expression.is_zero is not None

    def correct(self) -> bool | None:
        return self._expression.is_zero

    def get_node(self, index: int) -> BaseNode | None:
        node, index = self._index_to_node(self._expression, index)
        assert index >= 0, f"Invalid index for node: {index}"
        if node:
            return node
        if index == 0:
            return None

        for _, expr in self._definitions or []:
            node, index = self._index_to_node(expr, index)
            assert index >= 0, f"Invalid index for node: {index}"
            if node:
                return node
            if index == 0:
                return None

        return None

    def replace_node(self, index: int, new_node: BaseNode) -> 'State':
        raise NotImplementedError()


    def to_raw_state(self) -> np.ndarray:
        main_state, _ = self._to_node_state_array(
            context=MAIN_CONTEXT,
            subcontext=0,
            parent_node_idx=0,
            node_idx=1,
            node=self._expression,
        )

        definitions_state = self._to_context_items_array(
            context=DEFINITION_CONTEXT,
            expressions=[expr for _, expr in self._definitions or []],
        )

        assumptions_state = self._to_context_items_array(
            context=ASSUMPTION_CONTEXT,
            expressions=self._assumptions or [],
        )

        action_amount_state_list = []
        action_args_state_list = []

        for i, action_info in enumerate(self._action_types_args):
            action_amount_state_list.append(
                self._named_node_state_item(
                    context=ACTION_AMOUNT_CONTEXT,
                    subcontext=i,
                    parent_node_idx=0,
                    node_idx=1,
                    atomic_node=1,
                    node_type=0,
                    node_value=len(action_info.arg_types),
                )
            )

            for j, arg_type in enumerate(action_info.arg_types):
                action_args_state_list.append(
                    self._named_node_state_item(
                        context=ACTION_ARGS_CONTEXT,
                        subcontext=i,
                        parent_node_idx=0,
                        node_idx=j+1,
                        atomic_node=1,
                        node_type=arg_type,
                        node_value=0,
                    )
                )

        state = np.concatenate([
            main_state,
            definitions_state,
            assumptions_state,
            np.concatenate(action_amount_state_list),
            np.concatenate(action_args_state_list),
        ])

        return state

    def _to_context_items_array(self, context: int, expressions: list[BaseNode]) -> np.ndarray:
        nodes = np.array([], dtype=np.int_)

        for i, node in enumerate(expressions):
            context = DEFINITION_CONTEXT
            subcontext = i
            parent_node_idx = 0
            node_idx = parent_node_idx + 1

            iter_nodes, node_idx = self._to_node_state_array(
                context=context,
                subcontext=subcontext,
                parent_node_idx=parent_node_idx,
                node_idx=node_idx,
                node=node,
            )

            nodes = np.concatenate([
                nodes,
                iter_nodes,
            ])

        return nodes

    def _to_node_state_array(
        self,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: BaseNode,
    ) -> tuple[np.ndarray[np.int_, np.dtype], int]:
        node = self._expression

        state_array = np.array(self._to_leaf_state(
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            node=node,
        ))

        next_node_idx = node_idx + 1

        for arg in node.args:
            inner_node_array, next_node_idx = self._to_node_state_array(
                context=context,
                subcontext=subcontext,
                parent_node_idx=node_idx,
                node_idx=next_node_idx,
                node=arg,
            )

            state_array = np.concatenate([
                state_array,
                inner_node_array,
            ])

        return state_array, next_node_idx

    def _to_leaf_state(
        self,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: BaseNode,
    ) -> list[int]:
        handler = next(h for h in self._node_types if isinstance(node, h.node_type))
        assert handler is not None, f"Handler not found for node: {node}"
        atomic_node = len(node.args) == 0
        node_type = self._node_types.index(handler)
        node_value = handler.get_value(NodeValueParams(
            node=node,
            symbols=self._symbols,
            definition_keys=self._definition_keys,
        ))
        result = self._named_node_state_item(
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
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        atomic_node: int,
        node_type: int,
        node_value: int,
    ) -> list[int]:
        return [context, subcontext, parent_node_idx, node_idx, atomic_node, node_type, node_value]

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False

        my_definitions = self._definitions or []
        other_definitions = other._definitions or []

        if len(my_definitions) != len(other_definitions):
            return False

        definitions_to_replace = {
            other_definition: definition
            for (definition, _), (other_definition, _) in zip(my_definitions, other_definitions)
        }

        return self._expression == other._expression.subs(definitions_to_replace) and all(
            expr == other_expr.subs(definitions_to_replace)
            for (_, expr), (_, other_expr) in zip(my_definitions, other_definitions)
        )
