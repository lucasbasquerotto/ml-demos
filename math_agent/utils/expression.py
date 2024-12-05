from sympy import Dummy

def create_dummy(name: str | int) -> Dummy:
    return Dummy(name)