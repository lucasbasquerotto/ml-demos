"""
Token and Node definitions for extensible math agent.
Only built-in Python packages are used.
"""

from typing import Any, Dict, List, Optional, Callable

class Node:
    def __init__(self, name: str, args: Optional[List[Any]] = None):
        self.name = name
        self.args = args or []
    def __str__(self):
        if self.args:
            return f"{self.name}({', '.join(str(a) for a in self.args)})"
        return self.name
    def to_dict(self):
        return {'name': self.name, 'args': [a.to_dict() if isinstance(a, Node) else a for a in self.args]}

class NodeRegistry:
    def __init__(self):
        self.builtins: Dict[str, Callable] = {}
        self.custom: Dict[str, Callable] = {}
        self.allow_custom = False
    def register_builtin(self, name: str, func: Callable):
        self.builtins[name] = func
    def register_custom(self, name: str, func: Callable):
        if self.allow_custom:
            self.custom[name] = func
    def get(self, name: str):
        if name in self.builtins:
            return self.builtins[name]
        if self.allow_custom and name in self.custom:
            return self.custom[name]
        return None
    def set_custom_permission(self, allow: bool):
        self.allow_custom = allow
        if not allow:
            self.custom.clear()

# Example built-in nodes
registry = NodeRegistry()
def add(args):
    return args[0] + args[1]
def sub(args):
    return args[0] - args[1]
def mul(args):
    return args[0] * args[1]
def div(args):
    return args[0] / args[1] if args[1] != 0 else None
registry.register_builtin('Add', add)
registry.register_builtin('Sub', sub)
registry.register_builtin('Mul', mul)
registry.register_builtin('Div', div)

class Group(Node):
    def __init__(self, *args):
        super().__init__('Group', list(args))

class Assign(Node):
    def __init__(self, var, value):
        super().__init__('Assign', [var, value])

class Var(Node):
    def __init__(self, name):
        super().__init__('Var', [name])

class Function(Node):
    def __init__(self, name, args):
        super().__init__('Function', [name] + args)

# ... Add more nodes as needed
