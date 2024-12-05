from utils.types import Expression, Transformation, Dummy, Symbol, Integer
from utils.validator import is_zero
import numpy as np

MAIN_CONTEXT = 0
DUMMY_CONTEXT = 1
ASSUMPTION_CONTEXT = 2

UNKNOWN_TYPE = 0
DUMMY_TYPE = 1
FREE_SYMBOL_TYPE = 2
INTEGER_TYPE = 3

# context index (e.g: main expression, dummy expressions, assumptions)
# subcontext index (e.g: which dummy, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, dummy, integer, function/operator)
# node value (e.g: symbol index, dummy index, integer value, function/operator index)

class StateNode(Expression):
    def __init__(
        self,
        node_type: int
    ):
        self.node_type = node_type

class State:
    def __init__(
        self,
        expression: Expression,
        dummies: list[tuple[Dummy, Expression]] | None = None,
    ):
        self.expression = expression
        self.dummies = dummies
        self.dummy_keys = set([dummy for dummy, _ in dummies] if dummies else [])
        self.free_symbols = expression.free_symbols

    def terminal(self) -> bool:
        return is_zero(self.expression) is not None

    def correct(self) -> bool | None:
        return is_zero(self.expression) if self.terminal() else None

    def node_shallow_array(
        self,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: Expression,
    ) -> list[int]:
        node_value = 0

        if node.args:
            assert isinstance(node, StateNode)
            atomic_node = 0
            node_type = node.node_type
        else:
            atomic_node = 1

            if node in self.dummy_keys:
                node_type = DUMMY_TYPE
            elif isinstance(node, Symbol):
                node_type = FREE_SYMBOL_TYPE
            elif isinstance(node, Integer):
                node_type = INTEGER_TYPE
                # get sympy int value (as a python int)
                node_value = node.p
            else:
                raise ValueError(f"Unknown node type: {node}")

        return [context, subcontext, parent_node_idx, node_idx, atomic_node, node_type, node_value]


    def node_full_array(
        self,
        context: int,
        subcontext: int,
        parent_node_idx: int,
        node_idx: int,
        node: Expression,
    ) -> np.ndarray[int], int:
        node = self.expression

        node_array = np.array(self.node_shallow_array(
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            node=node,
        ))

        next_node_idx = node_idx + 1

        for arg in node.args:
            inner_node_array, next_node_idx = self.node_full_array(
                context=context,
                subcontext=subcontext,
                parent_node_idx=node_idx,
                node_idx=next_node_idx,
                node=arg,
            )

            node_array = np.concatenate([
                node_array,
                inner_node_array,
            ])

        return node_array, next_node_idx


    def state_array(self) -> np.ndarray:
        context = MAIN_CONTEXT
        subcontext = 0
        parent_node_idx = 0
        node_idx = parent_node_idx + 1
        node = self.expression

        nodes, _ = self.node_full_array(
            context=context,
            subcontext=subcontext,
            parent_node_idx=parent_node_idx,
            node_idx=node_idx,
            node=node,
        )

        for i, (_, dummy_expression) in enumerate(self.dummies or []):
            context = DUMMY_CONTEXT
            subcontext = i
            parent_node_idx = 0
            node_idx = parent_node_idx + 1
            node = dummy_expression

            dummy_nodes, node_idx = self.node_full_array(
                context=context,
                subcontext=subcontext,
                parent_node_idx=parent_node_idx,
                node_idx=node_idx,
                node=node,
            )

            nodes = np.concatenate([
                nodes,
                dummy_nodes,
            ])

        return nodes

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False

        my_dummies = self.dummies or []
        other_dummies = other.dummies or []

        if len(my_dummies) != len(other_dummies):
            return False

        dummies_to_replace = {
            other_dummy: dummy
            for (dummy, _), (other_dummy, _) in zip(my_dummies, other_dummies)
        }

        return self.expression == other.expression.subs(dummies_to_replace) and all(
            expr == other_expr.subs(dummies_to_replace)
            for (_, expr), (_, other_expr) in zip(my_dummies, other_dummies)
        )

class Action:
    def __init__(self, transformation: Transformation):
        self.transformation = transformation

class RewardEvaluator:
    def __call__(self, current_state: State, next_state: State) -> float:
        if next_state.terminal():
            return 100  # Contradiction reward (end of the episode)
        if next_state == current_state:
            return -10
        # Intermediate reward logic
        return -1  # Small penalty for each step taken

class Environment:
    def __init__(self, initial_expression: Expression, max_steps: int = 100000):
        self.initial_state = State(initial_expression)
        self.current_state = self.initial_state
        self.reward_evaluator = RewardEvaluator()
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self) -> State:
        self.current_state = self.initial_state
        self.current_step = 0
        return self.current_state

    def step(self, action: Action) -> tuple[State, float, bool, bool]:
        next_state = self.apply(self.current_state, action)
        reward = self.reward_evaluator(self.current_state, next_state)
        self.current_step += 1
        terminated = next_state.terminal()
        truncated = self.current_step >= self.max_steps and not terminated
        self.current_state = next_state
        return next_state, reward, terminated, truncated

    def apply(self, state: State, action: Action) -> State:
        # new_expression = apply_transformation(state.expression, action.transformation)
        # return State(new_expression)
        raise NotImplementedError("apply method is not implemented")
