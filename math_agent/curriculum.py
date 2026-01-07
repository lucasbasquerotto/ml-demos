"""
Adaptive curriculum for math agent.
Only built-in Python packages are used.
"""
from agent import Agent
from tokens import Node, Group, Assign, Var, Function

class Curriculum:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.level = 0
    def run_tests(self):
        # Simple tests for progression
        results = []
        # Level 0: Add
        n1 = Node('Add', [15, 30])
        results.append(self.agent.evaluate(n1) == 45)
        # Level 1: Assign and Var
        n2 = Group(Assign('x', 10), Assign('y', 20))
        self.agent.evaluate(n2)
        n3 = Node('Add', [Var('x'), Var('y')])
        results.append(self.agent.evaluate(n3) == 30)
        # Level 2: Function definition and use
        if self.agent.can_define_nodes():
            fdef = Function(
                'GreaterThan10',
                [Node('If', [Node('Greater', [Var('a'), 10]), Var('b'), Var('c')])])
            self.agent.define_function('GreaterThan10', fdef)
            # Simulate function call (not implemented yet)
        # ... Add more tests and unlocks as needed
        return results
    def advance(self):
        results = self.run_tests()
        if all(results):
            self.level += 1
            if self.level == 2:
                self.agent.set_custom_permission(True)
        return self.level
