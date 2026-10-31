"""COMPETIDOR 2 (parte 1): compilador de AST a bytecode para la maquina virtual."""
from __future__ import annotations
from enum import IntEnum
from typing import NamedTuple, Optional
from . import ast_nodes as A
from .tokens import FibLangError


class Op(IntEnum):
    PUSH = 0; LOAD = 1; STORE = 2
    ADD = 3; SUB = 4; MUL = 5
    LT = 6; GT = 7; EQ = 8; NE = 9; LE = 10; GE = 11
    JMPF = 12; JMP = 13; CALL = 14; RET = 15; PRINT = 16


BIN_TO_OP = {"+": Op.ADD, "-": Op.SUB, "*": Op.MUL, "<": Op.LT, ">": Op.GT,
             "==": Op.EQ, "!=": Op.NE, "<=": Op.LE, ">=": Op.GE}


class Instruction(NamedTuple):
    op: Op
    a: Optional[object] = None
    b: Optional[int] = None

    def __str__(self) -> str:
        parts = [self.op.name]
        if self.a is not None:
            parts.append(str(self.a))
        if self.b is not None:
            parts.append(str(self.b))
        return " ".join(parts)


class FunctionCode:
    def __init__(self, name: str, num_params: int) -> None:
        self.name = name
        self.num_params = num_params
        self.num_locals = num_params
        self.code: list[Instruction] = []


class BytecodeCompiler:
    def __init__(self, program: A.Program) -> None:
        self.program = program
        self.signatures = {f.name: len(f.params) for f in program.functions}

    def compile(self) -> dict[str, FunctionCode]:
        out = {}
        for f in self.program.functions:
            out[f.name] = self._compile_function(f.name, f.params, f.body)
        out["__main__"] = self._compile_function("__main__", [], self.program.main)
        return out

    def _compile_function(self, name, params, body) -> FunctionCode:
        fc = FunctionCode(name, len(params))
        slots = {p: i for i, p in enumerate(params)}
        code = fc.code

        def slot_for_store(n: str) -> int:
            if n not in slots:
                slots[n] = len(slots)
            return slots[n]

        def expr(e) -> None:
            if isinstance(e, A.Num):
                code.append(Instruction(Op.PUSH, e.value))
            elif isinstance(e, A.Var):
                if e.name not in slots:
                    raise FibLangError(f"Variable no definida: {e.name}")
                code.append(Instruction(Op.LOAD, slots[e.name]))
            elif isinstance(e, A.BinOp):
                expr(e.left); expr(e.right)
                code.append(Instruction(BIN_TO_OP[e.op]))
            elif isinstance(e, A.Call):
                if e.name not in self.signatures:
                    raise FibLangError(f"Funcion no definida: {e.name}")
                if len(e.args) != self.signatures[e.name]:
                    raise FibLangError(f"{e.name} espera {self.signatures[e.name]} argumentos")
                for a in e.args:
                    expr(a)
                code.append(Instruction(Op.CALL, e.name, len(e.args)))

        def stmts(lst) -> None:
            for s in lst:
                if isinstance(s, (A.Let, A.Assign)):
                    expr(s.expr)
                    code.append(Instruction(Op.STORE, slot_for_store(s.name)))
                elif isinstance(s, A.Print):
                    expr(s.expr); code.append(Instruction(Op.PRINT))
                elif isinstance(s, A.Return):
                    expr(s.expr); code.append(Instruction(Op.RET))
                elif isinstance(s, A.If):
                    expr(s.cond)
                    jf = len(code); code.append(Instruction(Op.JMPF, None))
                    stmts(s.then)
                    jend = len(code); code.append(Instruction(Op.JMP, None))
                    code[jf] = Instruction(Op.JMPF, len(code))
                    stmts(s.orelse)
                    code[jend] = Instruction(Op.JMP, len(code))

        stmts(body)
        code.append(Instruction(Op.PUSH, 0))   # return implicito
        code.append(Instruction(Op.RET))
        fc.num_locals = len(slots)
        return fc


def disassemble(compiled: dict[str, FunctionCode]) -> str:
    lines = []
    for fc in compiled.values():
        lines.append(f"{fc.name}  (params={fc.num_params}, locales={fc.num_locals})")
        for i, ins in enumerate(fc.code):
            lines.append(f"  {i:03d}  {ins}")
    return "\n".join(lines)
