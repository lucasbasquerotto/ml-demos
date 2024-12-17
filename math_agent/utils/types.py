import sympy

BaseNode = sympy.Basic

Assumption = sympy.Basic

class IdElem(sympy.Basic):
    @classmethod
    def prefix(cls):
        return 'unk'

    def __init__(self, id: int):
        super().__init__()
        self._args = (sympy.Integer(id), sympy.Dummy())

    def _latex(self, printer): # pylint: disable=unused-argument
        return r"%s_{%s}" % (self.prefix(), self.args[0])

    @property
    def id(self) -> int:
        id = self.args[0]
        assert isinstance(id, sympy.Integer)
        return int(id)

class FunctionDefinition(IdElem):
    @classmethod
    def prefix(cls):
        return 'f'

class ParamVar(IdElem):
    @classmethod
    def prefix(cls):
        return 'p'
