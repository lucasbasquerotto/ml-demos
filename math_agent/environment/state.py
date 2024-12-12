from utils.types import BaseNode, DefinitionKey, Assumption

class State:
    def __init__(
        self,
        expression: BaseNode,
        definitions: tuple[tuple[DefinitionKey, BaseNode], ...] | None = None,
        partial_definitions: tuple[tuple[DefinitionKey, BaseNode | None], ...] | None = None,
        assumptions: tuple[Assumption, ...] | None = None,
    ):
        self._expression = expression
        self._definitions = definitions
        self._partial_definitions = partial_definitions
        self._assumptions = assumptions

    @property
    def expression(self) -> BaseNode:
        return self._expression

    @property
    def definitions(self) -> tuple[tuple[DefinitionKey, BaseNode], ...] | None:
        return self._definitions

    @property
    def partial_definitions(self) -> tuple[tuple[DefinitionKey, BaseNode | None], ...] | None:
        return self._partial_definitions

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
        root: BaseNode,
        index: int,
        new_node: BaseNode,
    ) -> tuple[BaseNode | None, int]:
        assert root is not None
        assert index > 0, f"Invalid index for root node: {index}"
        assert isinstance(index, int), f"Invalid index type for root node: {type(index)} ({index})"
        index -= 1

        if index == 0:
            return new_node, index

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
        definitions: list[BaseNode] = [
            expr
            for _, expr in self.definitions or []]
        partial_definitions: list[BaseNode] = [
            expr
            for _, expr in self.partial_definitions or []
            if expr is not None]

        for expr in [self.expression] + definitions + partial_definitions:
            node, index, child_index = self._index_to_node(
                root=expr, index=index, parent=parent)
            assert index >= 0, f"Invalid index for node: {index}"
            if index == 0:
                return node, child_index

        return None, None

    def get_node(self, index: int) -> BaseNode | None:
        node, _ = self._get_node(index=index)
        return node

    def apply_new_node(self, expr_id: int, new_node: BaseNode) -> 'State':
        assert expr_id is not None, "Empty expression id"
        assert expr_id > 0, f"Invalid expression id: {expr_id}"

        index = expr_id

        new_root, index = self._replace_node_index(
            root=self.expression, index=index, new_node=new_node)
        assert index >= 0, f"Invalid index for node: {index}"
        if index == 0:
            assert new_root is not None, "Invalid new root node"
            return State(
                expression=new_root,
                definitions=self.definitions,
                partial_definitions=self.partial_definitions,
                assumptions=self.assumptions)

        definitions_list = list(self.definitions or [])
        for i, (key, expr) in enumerate(definitions_list):
            new_root, index = self._replace_node_index(
                root=expr, index=index, new_node=new_node)
            assert index >= 0, f"Invalid index for node: {index}"
            if index == 0:
                assert new_root is not None, "Invalid new root node (definition)"
                definitions_list[i] = (key, new_root)
                return State(
                    expression=self.expression,
                    definitions=tuple(definitions_list),
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
                        expression=self.expression,
                        definitions=self.definitions,
                        partial_definitions=tuple(partial_definitions_list),
                        assumptions=self.assumptions)

        raise ValueError(f"Invalid expr_id: {expr_id}")

    def __eq__(self, other) -> bool:
        if not isinstance(other, State):
            return False

        my_definitions = self._definitions or tuple()
        other_definitions = other._definitions or tuple()

        if len(my_definitions) != len(other_definitions):
            return False

        definitions_to_replace = {
            other_definition: definition
            for (definition, _), (other_definition, _) in zip(my_definitions, other_definitions)
        }

        return self._expression == other._expression.subs(definitions_to_replace) and all(
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
