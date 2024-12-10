import typing
from utils.types import BaseNode, DefinitionKey, Assumption, ActionOutput

MAIN_CONTEXT = 0
DEFINITION_CONTEXT = 1
ASSUMPTION_CONTEXT = 2
ACTION_AMOUNT_CONTEXT = 3
ACTION_ARGS_CONTEXT = 4

T = typing.TypeVar("T", bound=BaseNode)
V = typing.TypeVar("V", bound=int | float)

# context index (e.g: main expression, definition expressions, assumptions)
# subcontext index (e.g: which definition, which equality, which assumption)
# parent node index (0 for the root node of an expression)
# atomic node (whether the node is atomic (no args, no operation) or not)
# node type index (e.g: symbol/unknown, definition, integer, function/operator)
# node value (e.g: symbol index, definition index, integer value, function/operator index)

class NodeValueParams(typing.Generic[T]):
    def __init__(self, node: T, symbols: list[BaseNode], definition_keys: list[DefinitionKey]):
        self.node = node
        self.symbols = symbols
        self.definition_keys = definition_keys

class NodeTypeHandler(typing.Generic[T, V]):
    def __init__(
        self,
        node_type: typing.Type[T],
        get_value: typing.Callable[[NodeValueParams[T]], V],
    ):
        self.node_type = node_type
        self.get_value = get_value

class State:
    def __init__(
        self,
        expression: BaseNode,
        definitions: list[tuple[DefinitionKey, BaseNode]] | None = None,
        assumptions: list[Assumption] | None = None,
    ):
        self._expression = expression
        self._definitions = definitions
        self._assumptions = assumptions

    @property
    def expression(self) -> BaseNode:
        return self._expression

    @property
    def definitions(self) -> list[tuple[DefinitionKey, BaseNode]] | None:
        return self._definitions

    @property
    def assumptions(self) -> list[Assumption] | None:
        return self._assumptions

    @classmethod
    def index_to_node(cls, root: BaseNode, index: int) -> BaseNode | None:
        node, _ = cls._index_to_node(root, index)
        return node

    @classmethod
    def _index_to_node(cls, root: BaseNode, index: int) -> tuple[BaseNode | None, int]:
        assert index > 0, f"Invalid index for root node: {index}"
        assert isinstance(index, int), f"Invalid index type for root node: {type(index)} ({index})"
        index -= 1
        node: BaseNode | None = root

        if index > 0:
            for arg in root.args:
                # recursive call each node arg to traverse its subtree
                node, index = cls._index_to_node(root=arg, index=index)
                assert index >= 0, f"Invalid index for node: {index}"
                # it will end when index = 0 (it's the actual node, if any)
                # otherwise, it will go to the next arg
                if index == 0:
                    break

        return node if (index == 0) else None, index

    def get_node(self, index: int) -> BaseNode | None:
        node, index = self._index_to_node(self.expression, index)
        assert index >= 0, f"Invalid index for node: {index}"
        if node:
            return node
        if index == 0:
            return None

        for _, expr in self.definitions or []:
            node, index = self._index_to_node(expr, index)
            assert index >= 0, f"Invalid index for node: {index}"
            if node:
                return node
            if index == 0:
                return None

        return None

    def apply(self, action: ActionOutput) -> 'State':
        # node_idx = action.node_idx
        # new_node = action.new_node
        raise NotImplementedError()
