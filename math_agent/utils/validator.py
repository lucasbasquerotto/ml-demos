import sympy as sp

def validate_expression(expression: str) -> bool:
    try:
        sp.sympify(expression)
        return True
    except sp.SympifyError:
        return False

def validate_transformation(expression: str, transformation: str) -> bool:
    try:
        expr = sp.sympify(expression)
        transformed_expr = sp.sympify(transformation)
        return expr.equals(transformed_expr)
    except sp.SympifyError:
        return False

def is_zero(expression: sp.Expr) -> bool | None:
    return expression.equals(0)
