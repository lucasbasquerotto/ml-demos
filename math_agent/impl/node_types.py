import sympy

class Add(sympy.Expr):
    def __new__(cls, *args):
        super().__new__(cls, *args)

    def doit(self, **hints):
        return sympy.Add(*self.args).doit(**hints)

    def _eval_nseries(self, x, n, logx, cdir):
        return sympy.Add(*self.args).series(x, n, logx, cdir)
