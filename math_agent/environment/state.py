from utils.types import Expression
from utils.validator import is_contradictory_expression
from utils.expression_parser import parse_expression

class State:
    def __init__(self, expression: str):
        self.expression: Expression = parse_expression(expression)

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False
        return self.expression.equals(other.expression)

    def is_contradictory(self) -> bool:
        return is_contradictory_expression(self.expression)
