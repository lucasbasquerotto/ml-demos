"""
Simple extensible agent for math/logical expressions.
Only built-in Python packages are used.
"""
from typing import Any
from tokens import Node, registry

class Agent:
    def __init__(self):
        self.vars: dict[Any, Any] = {}
        self.functions: dict[str, Node] = {}
        self.registry = registry
    def set_custom_permission(self, allow: bool):
        self.registry.set_custom_permission(allow)
    def define_function(self, name: str, node: Node):
        if self.registry.allow_custom:
            self.functions[name] = node
            self.registry.register_custom(name, lambda args: self.evaluate(node))
    def assign(self, var, value):
        self.vars[var] = value
    def evaluate(self, node: Node):
        if node.name == 'Group':
            return [self.evaluate(n) for n in node.args]
        elif node.name == 'Assign':
            var, value = node.args
            val = self.evaluate(value)
            self.assign(var, val)
            return val
        elif node.name == 'Var':
            name = node.args[0]
            return self.vars.get(name, None)
        elif node.name == 'Function':
            fname = node.args[0]
            fargs = [self.evaluate(a) for a in node.args[1:]]
            func = self.registry.get(fname)
            if func:
                return func(fargs)
            return None
        else:
            # Built-in or custom node
            func = self.registry.get(node.name)
            if func:
                eval_args = [self.evaluate(a) for a in node.args]
                return func(eval_args)
            return None
    def can_define_nodes(self):
        return self.registry.allow_custom
