import sympy
from utils.types import BaseNode, FunctionDefinition, ParamVar, Assumption

class ExprInfo:
    def __init__(self, expr: BaseNode, params: tuple[ParamVar, ...]):
        self._expr = expr
        self._params = params

    @property
    def expr(self) -> BaseNode:
        return self._expr

    @property
    def params(self) -> tuple[ParamVar, ...]:
        return self._params

class ArgGroup:
    def __init__(self, amount, expressions: tuple[ExprInfo | None, ...]):
        assert amount == len(expressions), \
            f"Invalid amount of expressions: {amount} != {len(expressions)}"
        self._amount = amount
        self._expressions = expressions

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def expressions(self) -> tuple[ExprInfo | None, ...]:
        return self._expressions

class ExprWithArgs:
    def __init__(self, expr_info: ExprInfo, args: tuple[BaseNode, ...]):
        assert len(expr_info.params) == len(args), \
            f"Invalid amount of arguments: {len(expr_info.params)} != {len(args)}"

        args_dict: dict[ParamVar, BaseNode] = {
            p: args[i]
            for i, p in enumerate(expr_info.params)
        }

        self._expr_info = expr_info
        self._args = args
        self._args_dict = args_dict

    @property
    def expr(self) -> BaseNode:
        return self._expr_info.expr

    @property
    def args(self) -> tuple[BaseNode, ...]:
        return self._args

    @property
    def apply(self) -> BaseNode:
        return self.expr.subs(self._args_dict)

class State:
    def __init__(
        self,
        definitions: tuple[tuple[FunctionDefinition, ExprInfo], ...] | None,
        partial_definitions: tuple[tuple[FunctionDefinition, ExprInfo | None], ...] | None,
        arg_groups: tuple[ArgGroup, ...] | None,
        assumptions: tuple[Assumption, ...] | None,
    ):
        self._definitions = definitions
        self._partial_definitions = partial_definitions
        self._arg_groups = arg_groups
        self._assumptions = assumptions

    @property
    def definitions(self) -> tuple[tuple[FunctionDefinition, ExprInfo], ...] | None:
        return self._definitions

    @property
    def partial_definitions(self) -> tuple[tuple[FunctionDefinition, ExprInfo | None], ...] | None:
        return self._partial_definitions

    @property
    def arg_groups(self) -> tuple[ArgGroup, ...] | None:
        return self._arg_groups

    @property
    def assumptions(self) -> tuple[Assumption, ...] | None:
        return self._assumptions

    @classmethod
    def index_to_node(cls, root: BaseNode, index: int) -> BaseNode | None:
        node, _, __ = cls._index_to_node(root, index, parent=False)
        return node

    @classmethod
    def _index_to_node(
        cls,
        root: BaseNode,
        index: int,
        parent: bool,
        parent_node: BaseNode | None = None,
        child_index: int | None = None,
    ) -> tuple[BaseNode | None, int, int | None]:
        assert root is not None
        assert index > 0, f"Invalid index for root node: {index}"
        assert isinstance(index, int), f"Invalid index type for root node: {type(index)} ({index})"
        index -= 1
        node: BaseNode | None = root

        if index > 0:
            parent_node = root
            for i, arg in enumerate(root.args):
                # recursive call each node arg to traverse its subtree
                node, index, child_index = cls._index_to_node(
                    root=arg,
                    index=index,
                    parent=parent,
                    parent_node=parent_node,
                    child_index=i)
                assert index >= 0, f"Invalid index for node: {index}"
                # it will end when index = 0 (it's the actual node, if any)
                # otherwise, it will go to the next arg
                if index == 0:
                    break

        return (parent_node if parent else node) if (index == 0) else None, index, child_index

    @classmethod
    def _replace_node_index(
        cls,
        root: BaseNode | None,
        index: int,
        new_node: BaseNode,
    ) -> tuple[BaseNode | None, int]:
        assert index > 0, f"Invalid index for root node: {index}"
        assert isinstance(index, int), f"Invalid index type for root node: {type(index)} ({index})"
        index -= 1

        if index == 0:
            return new_node, index

        assert root is not None, f"Invalid root node for index {index}"

        args_list: list[BaseNode] = list(root.args)

        for i, arg in enumerate(args_list):
            # recursive call each node arg to traverse its subtree
            new_arg, index = cls._replace_node_index(
                root=arg,
                index=index,
                new_node=new_node)
            assert index >= 0, f"Invalid index for node: {index}"
            # it will end when index = 0 (it's the actual node, if any)
            # otherwise, it will go to the next arg
            # it returns the actual arg subtree with the new node
            if index == 0:
                assert new_arg is not None, "Invalid new arg node"
                args_list[i] = new_arg
                return root.func(*args_list), index

        return None, index

    def _get_node(
        self,
        index: int,
        parent: bool = False,
    ) -> tuple[BaseNode | None, int | None]:
        initial_index = index
        definitions: list[ExprInfo] = [
            expr
            for _, expr in self.definitions or []]
        partial_definitions: list[ExprInfo] = [
            expr
            for _, expr in self.partial_definitions or []
            if expr is not None]
        arg_exprs: list[ExprInfo] = [
            expr
            for group in self.arg_groups or []
            for expr in group.expressions
            if expr is not None]

        for expr in definitions + partial_definitions + arg_exprs:
            node, index, child_index = self._index_to_node(
                root=expr, index=index, parent=parent)
            assert index >= 0, f"Invalid index for node: {initial_index}"
            if index == 0:
                return node, child_index

        return None, None

    def get_node(self, index: int) -> BaseNode | None:
        node, _ = self._get_node(index=index)
        return node

    def get_expression_node_info(
        self,
        root: BaseNode | None,
        node_idx: int,
    ) -> tuple[BaseNode | None, BaseNode | None, int | None]:
        if node_idx == 1:
            return root, None, None

        assert root is not None, "Invalid root"

        index = node_idx

        parent_node, index, child_index = self._index_to_node(
            root=root, index=index, parent=True)

        assert index >= 0, f"Invalid index for node: {node_idx}"
        if index == 0:
            assert parent_node is not None, "Invalid parent node"
            assert child_index is not None, "Invalid child index"
            node = parent_node.args[child_index]
            return node, parent_node, child_index

        return None, None, None

    def change_partial_definition(
        self,
        partial_definition_idx: int,
        node_idx: int,
        new_node_info: ExprInfo,
    ) -> 'State':
        partial_definitions_list = list(self.partial_definitions or [])
        assert partial_definition_idx >= 0, \
            f"Invalid partial definition: {partial_definition_idx}"
        assert partial_definition_idx < len(partial_definitions_list), \
            f"Invalid partial definition: {partial_definition_idx}"
        key, root = partial_definitions_list[partial_definition_idx]
        new_root, index = self._replace_node_index(
            root=root.expr,
            index=node_idx,
            new_node=new_node_info.expr.subs(new_node_info.params.dict()))
        assert index == 0, f"Node {node_idx} not found " \
            + f"in partial definition: {partial_definition_idx}"
        assert new_root is not None, "Invalid new root node"
        partial_definitions_list[partial_definition_idx] = (key, new_root)
        return State(
            definitions=self.definitions,
            partial_definitions=tuple(partial_definitions_list),
            arg_groups=self.arg_groups,
            assumptions=self.assumptions)

    def change_arg(
        self,
        arg_group_id: int,
        arg_id: int,
        node_idx: int,
        new_node: BaseNode,
    ) -> 'State':
        arg_group_idx = arg_group_id - 1
        arg_idx = arg_id - 1
        arg_groups_list = list(self.arg_groups or [])
        assert arg_group_idx >= 0, f"Invalid arg group: {arg_group_id}"
        assert arg_group_idx < len(arg_groups_list), f"Invalid arg group: {arg_group_id}"
        arg_group = arg_groups_list[arg_group_idx]
        expressions = list(arg_group.expressions)
        assert arg_group.amount == len(expressions), \
            f"Invalid amount of expressions: {arg_group.amount} != {len(expressions)}"
        assert arg_idx >= 0, f"Invalid arg: {arg_id}"
        assert arg_idx < len(arg_group.expressions), f"Invalid arg: {arg_id}"
        expression = expressions[arg_idx]
        new_root, index = self._replace_node_index(
            root=expression,
            index=node_idx,
            new_node=new_node)
        assert index == 0, f"Node {node_idx} not found in arg: " \
            + f"{arg_id} (group: {arg_group_id})"
        assert new_root is not None, "Invalid new root node"
        expressions[arg_idx] = new_root
        arg_groups_list[arg_group_idx] = ArgGroup(
            amount=arg_group.amount,
            expressions=tuple(expressions))
        return State(
            definitions=self.definitions,
            partial_definitions=self.partial_definitions,
            arg_groups=tuple(arg_groups_list),
            assumptions=self.assumptions)

    def apply_new_node(self, expr_id: int, new_node: BaseNode) -> 'State':
        assert expr_id is not None, "Empty expression id"
        assert expr_id > 0, f"Invalid expression id: {expr_id}"

        index = expr_id

        definitions_list = list(self.definitions or [])
        for i, (key, expr) in enumerate(definitions_list):
            new_root, index = self._replace_node_index(
                root=expr, index=index, new_node=new_node)
            assert index >= 0, f"Invalid index for node: {index}"
            if index == 0:
                assert new_root is not None, "Invalid new root node (definition)"
                definitions_list[i] = (key, new_root)
                return State(
                    definitions=tuple(definitions_list),
                    partial_definitions=self.partial_definitions,
                    arg_groups=self.arg_groups,
                    assumptions=self.assumptions)

        partial_definitions_list = list(self.partial_definitions or [])
        for i, (key, expr_p) in enumerate(partial_definitions_list):
            if expr_p is not None:
                expr = expr_p
                new_root, index = self._replace_node_index(
                    root=expr, index=index, new_node=new_node)
                assert index >= 0, f"Invalid index for node: {index}"
                if index == 0:
                    assert new_root is not None, "Invalid new root node (partial definition)"
                    partial_definitions_list[i] = (key, new_root)
                    return State(
                        definitions=self.definitions,
                        partial_definitions=tuple(partial_definitions_list),
                        arg_groups=self.arg_groups,
                        assumptions=self.assumptions)

        arg_groups_list = list(self.arg_groups or [])
        for i, arg_group in enumerate(arg_groups_list):
            expressions = list(arg_group.expressions)
            for j, expr_p in enumerate(expressions):
                if expr_p is not None:
                    expr = expr_p
                    new_root, index = self._replace_node_index(
                        root=expr, index=index, new_node=new_node)
                    assert index >= 0, f"Invalid index for node: {index}"
                    if index == 0:
                        assert new_root is not None, "Invalid new root node (arg)"
                        expressions[j] = new_root
                        arg_groups_list[i] = ArgGroup(
                            amount=arg_group.amount,
                            expressions=tuple(expressions))
                        return State(
                            definitions=self.definitions,
                            partial_definitions=self.partial_definitions,
                            arg_groups=tuple(arg_groups_list),
                            assumptions=self.assumptions)

        raise ValueError(f"Invalid expr_id: {expr_id}")

    @classmethod
    def same_definitions(
        cls,
        my_definitions: tuple[tuple[FunctionDefinition, BaseNode | None], ...] | None,
        other_definitions: tuple[tuple[FunctionDefinition, BaseNode | None], ...] | None,
    ) -> bool:
        my_definitions = my_definitions or tuple()
        other_definitions = other_definitions or tuple()

        if len(my_definitions) != len(other_definitions):
            return False

        definitions_to_replace = {
            other_definition: definition
            for (definition, _), (other_definition, _) in zip(my_definitions, other_definitions)
        }

        return all(
            (expr == other_expr == None)
            or
            (
                expr is not None
                and
                other_expr is not None
                and
                expr == other_expr.subs(definitions_to_replace)
            )
            for (_, expr), (_, other_expr) in zip(my_definitions, other_definitions)
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False

        same_definitions = self.same_definitions(
            self.definitions,
            other.definitions)

        if not same_definitions:
            return False

        same_partial_definitions = self.same_definitions(
            self.partial_definitions,
            other.partial_definitions)

        if not same_partial_definitions:
            return False

        # TODO

        return True
