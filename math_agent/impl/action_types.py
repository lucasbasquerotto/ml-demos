import sympy
from utils.types import (
    ActionOutput,
    SameValueNodeActionOutput,
    NewPartialDefinitionActionOutput,
    NewDefinitionFromPartialActionOutput,
    NewDefinitionFromNodeActionOutput,
    ReplaceByDefinitionActionOutput,
    ApplyDefinitionActionOutput,
    UpdatePartialDefinitionActionOutput)
from environment.action import (
    InvalidActionArgException,
    InvalidActionArgsException,
)
from environment.state import State
from impl.base_action_types import (
    EmptyArgsAction,
    SingleNodeAction,
    DefinitionNodeAction,
    DoubleChildAction)

class NewDefinitionAction(EmptyArgsAction):

    def output(self, state: State) -> ActionOutput:
        partial_definition_idx = len(state.partial_definitions or [])
        return NewPartialDefinitionActionOutput(partial_definition_idx=partial_definition_idx)

class DefinitionToNodeAction(DefinitionNodeAction):

    def output(self, state: State) -> ActionOutput:
        definition_idx = self.definition_idx
        expr_id = self.expr_id
        definitions = state.definitions
        if definitions is None:
            raise InvalidActionArgException("No definitions yet")
        if definition_idx < 0 or definition_idx >= len(state.definitions or []):
            raise InvalidActionArgException(f"Invalid definition index: {definition_idx}")
        key, definition_node = definitions[definition_idx]
        if not definition_node:
            raise InvalidActionArgException(f"Definition {definition_idx} has no expression")
        target_node = state.get_node(expr_id)
        if not target_node:
            raise InvalidActionArgException(f"Invalid target node index: {expr_id}")
        if key != target_node:
            raise InvalidActionArgException(
                f"Invalid target node: {target_node} (expected {key})")
        return SameValueNodeActionOutput(expr_id=expr_id, new_node=definition_node)

class NodeToDefinitionAction(SingleNodeAction):

    def output(self, state: State) -> ActionOutput:
        expr_id = self.expr_id
        node = state.get_node(expr_id)
        if not node:
            raise InvalidActionArgException(f"Invalid node index: {expr_id}")
        definition_idx = len(state.definitions or [])
        return NewDefinitionFromNodeActionOutput(
            definition_idx=definition_idx,
            expr_id=expr_id)

class SimplifyAddAction(DoubleChildAction):

    def output(self, state: State) -> ActionOutput:
        parent_expr_id = self.parent_expr_id
        arg1 = self.arg1
        arg2 = self.arg2

        parent_node = state.get_node(parent_expr_id)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_expr_id}")
        if not isinstance(parent_node, sympy.Add):
            raise InvalidActionArgException(f"Invalid parent node type: {type(parent_node)}")
        if not isinstance(arg1, int):
            raise InvalidActionArgsException(f"Invalid arg1 type: {type(arg1)}")
        if arg1 == arg2:
            raise InvalidActionArgsException(f"Invalid arg2 type: {type(arg2)}")
        if arg1 < 0 or arg2 < 0:
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
        if arg1 > len(parent_node.args) or arg2 > len(parent_node.args):
            raise InvalidActionArgsException(
                f"Invalid arg1 or arg2 max value: {arg1}, {arg2} (max {len(parent_node.args)})")

        node1 = parent_node.args[arg1]
        node2 = parent_node.args[arg2]

        if not isinstance(node1, sympy.Expr):
            raise InvalidActionArgsException(f"Invalid node1 type: {type(node1)}")
        if not isinstance(node2, sympy.Expr):
            raise InvalidActionArgsException(f"Invalid node2 type: {type(node2)}")


        if node1 != -node2:
            raise InvalidActionArgsException(
                "Invalid node1 or node2 value "
                + "(should be the same expression with opposite values): "
                + f"{node1}, {node2}")

        new_args = [arg for i, arg in enumerate(parent_node.args) if i not in [arg1, arg2]]

        if not new_args:
            return SameValueNodeActionOutput(expr_id=parent_expr_id, new_node=sympy.Integer(0))
        if len(new_args) == 1:
            return SameValueNodeActionOutput(expr_id=parent_expr_id, new_node=new_args[0])
        return SameValueNodeActionOutput(expr_id=parent_expr_id, new_node=sympy.Add(*new_args))

class SwapAddAction(DoubleChildAction):

    def output(self, state: State) -> ActionOutput:
        parent_expr_id = self.parent_expr_id
        arg1 = self._arg1
        arg2 = self._arg2

        parent_node = state.get_node(parent_expr_id)

        if not parent_node:
            raise InvalidActionArgException(f"Invalid parent node index: {parent_expr_id}")
        if not isinstance(parent_node, sympy.Add):
            raise InvalidActionArgException(f"Invalid parent node type: {type(parent_node)}")
        if not isinstance(arg1, int) or not isinstance(arg2, int):
            raise InvalidActionArgsException(
                f"Invalid arg1 or arg2 type: {type(arg1)}, {type(arg2)}")
        if arg1 < 0 or arg2 < 0:
            raise InvalidActionArgsException(f"Invalid arg1 or arg2 min value: {arg1}, {arg2}")
        if arg1 >= len(parent_node.args) or arg2 >= len(parent_node.args):
            raise InvalidActionArgsException(
                "Invalid arg1 or arg2 max value: "
                + f"{arg1}, {arg2} (max {len(parent_node.args) - 1})")

        new_args = list(parent_node.args)
        new_args[arg1], new_args[arg2] = new_args[arg2], new_args[arg1]

        return SameValueNodeActionOutput(expr_id=parent_expr_id, new_node=sympy.Add(*new_args))
