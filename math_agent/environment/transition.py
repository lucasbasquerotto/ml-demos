from utils.types import Expression, Equality, Transformation
from .state import State
from .action import Action

def apply_transformation(expression: Expression, transformation: Transformation) -> Expression:
    if not isinstance(transformation, Equality):
        raise ValueError("Transformation must be an equation")
    return expression.subs(transformation.lhs, transformation.rhs)

class Transition:
    def apply(self, state: State, action: Action) -> State:
        new_expression = apply_transformation(state.expression, action.transformation)
        return State(str(new_expression))
