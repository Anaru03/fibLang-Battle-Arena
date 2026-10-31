"""COMPETIDOR 2 (parte 2): maquina virtual de pila."""
from __future__ import annotations
from typing import Callable, Optional
from .bytecode import FunctionCode, Op


class VirtualMachine:
    def __init__(self, compiled: dict[str, FunctionCode], out: Callable = print) -> None:
        self.compiled = compiled
        self.out = out

    def run(self, trace: Optional[Callable[[str, int, list], None]] = None) -> None:
        """Ejecuta __main__. Si se pasa `trace`, se llama antes de cada
        instruccion con (instruccion, pc, pila): ideal para animar la pila."""
        # constantes locales: acceso mas rapido dentro del ciclo caliente
        PUSH, LOAD, STORE, ADD, SUB, MUL = Op.PUSH, Op.LOAD, Op.STORE, Op.ADD, Op.SUB, Op.MUL
        LT, GT, EQ, NE, LE, GE = Op.LT, Op.GT, Op.EQ, Op.NE, Op.LE, Op.GE
        JMPF, JMP, CALL, RET, PRINT = Op.JMPF, Op.JMP, Op.CALL, Op.RET, Op.PRINT

        stack: list = []
        push, pop = stack.append, stack.pop
        frames: list = []
        compiled = self.compiled
        main = compiled["__main__"]
        code, pc, loc = main.code, 0, [0] * main.num_locals

        while True:
            ins = code[pc]
            if trace:
                trace(str(ins), pc, list(stack))
            pc += 1
            op, a, b = ins
            if op is PUSH:
                push(a)
            elif op is LOAD:
                push(loc[a])
            elif op is SUB:
                y = pop(); stack[-1] -= y
            elif op is ADD:
                y = pop(); stack[-1] += y
            elif op is LT:
                y = pop(); stack[-1] = int(stack[-1] < y)
            elif op is JMPF:
                if not pop():
                    pc = a
            elif op is CALL:
                fc = compiled[a]
                new = [0] * fc.num_locals
                for i in range(b - 1, -1, -1):
                    new[i] = pop()
                frames.append((code, pc, loc))
                code, pc, loc = fc.code, 0, new
            elif op is RET:
                if not frames:
                    return
                code, pc, loc = frames.pop()
            elif op is STORE:
                loc[a] = pop()
            elif op is JMP:
                pc = a
            elif op is MUL:
                y = pop(); stack[-1] *= y
            elif op is GT:
                y = pop(); stack[-1] = int(stack[-1] > y)
            elif op is EQ:
                y = pop(); stack[-1] = int(stack[-1] == y)
            elif op is NE:
                y = pop(); stack[-1] = int(stack[-1] != y)
            elif op is LE:
                y = pop(); stack[-1] = int(stack[-1] <= y)
            elif op is GE:
                y = pop(); stack[-1] = int(stack[-1] >= y)
            elif op is PRINT:
                self.out(pop())
