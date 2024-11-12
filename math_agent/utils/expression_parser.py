import sympy as sp

def parse_expression(expression: str) -> sp.Basic:
    try:
        return sp.sympify(expression)
    except Exception as exc:
        raise ValueError("Invalid mathematical expression") from exc

def apply_transformation(expression: str, transformation: str) -> sp.Basic:
    expr = parse_expression(expression)
    trans = parse_expression(transformation)
    if not isinstance(trans, sp.Equality):
        raise ValueError("Transformation must be an equation")
    return expr.subs(trans.lhs, trans.rhs)
