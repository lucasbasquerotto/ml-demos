import sympy as sp
from .types import Expression, Transformation

def parse_expression(expression: str) -> Expression:
    try:
        return sp.sympify(expression)
    except Exception as exc:
        raise ValueError(f"Invalid mathematical expression: {expression}") from exc

def apply_transformation(expression: Expression, transformation: Transformation) -> Expression:
    if not isinstance(transformation, sp.Equality):
        raise ValueError(f"Transformation must be an equation: {transformation}")
    return expression.subs(transformation.lhs, transformation.rhs)
