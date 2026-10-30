"""COMPETIDOR 1: interprete de arbol (recorre el AST y evalua directamente)."""
from __future__ import annotations
from typing import Callable
from . import ast_nodes as A
from .tokens import FibLangError

_NO_RETURN = object()   # marca: "la sentencia no ejecuto return"

BINARY_OPS = {
    "+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b,
    "<": lambda a, b: int(a < b), ">": lambda a, b: int(a > b),
    "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b),
    "<=": lambda a, b: int(a <= b), ">=": lambda a, b: int(a >= b),
}


class TreeInterpreter:
    def __init__(self, program: A.Program, out: Callable = print) -> None:
        self.program = program
        self.out = out
        self.functions = {f.name: f for f in program.functions}
        self._eval_table = {
            A.Num: self._num, A.Var: self._var,
            A.BinOp: self._binop, A.Call: self._call,
        }

    def run(self) -> None:
        self._exec_block(self.program.main, {})

    # ---- expresiones
    def _eval(self, e, env):
        return self._eval_table[type(e)](e, env)

    def _num(self, e, env):
        return e.value

    def _var(self, e, env):
        try:
            return env[e.name]
        except KeyError:
            raise FibLangError(f"Variable no definida: {e.name}") from None

    def _binop(self, e, env):
        return BINARY_OPS[e.op](self._eval(e.left, env), self._eval(e.right, env))

    def _call(self, e, env):
        fn = self.functions.get(e.name)
        if fn is None:
            raise FibLangError(f"Funcion no definida: {e.name}")
        if len(e.args) != len(fn.params):
            raise FibLangError(f"{e.name} espera {len(fn.params)} argumentos")
        local = {p: self._eval(a, env) for p, a in zip(fn.params, e.args)}
        r = self._exec_block(fn.body, local)
        return 0 if r is _NO_RETURN else r

    # ---- sentencias
    def _exec_block(self, stmts, env):
        for s in stmts:
            t = type(s)
            if t is A.Return:
                return self._eval(s.expr, env)
            if t is A.If:
                branch = s.then if self._eval(s.cond, env) else s.orelse
                r = self._exec_block(branch, env)
                if r is not _NO_RETURN:
                    return r
            elif t is A.Let or t is A.Assign:
                env[s.name] = self._eval(s.expr, env)
            elif t is A.Print:
                self.out(self._eval(s.expr, env))
        return _NO_RETURN
