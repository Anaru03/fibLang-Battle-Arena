"""Benchmark justo: mismo programa, misma maquina, varias repeticiones (mediana)."""
from __future__ import annotations
import statistics
import subprocess
import tempfile
import time
from dataclasses import dataclass
from . import ast_nodes as A
from .bytecode import BytecodeCompiler
from .cgen import NativeBuilder
from .interpreter import TreeInterpreter
from .vm import VirtualMachine


@dataclass
class Result:
    name: str
    prep_seconds: float
    exec_seconds: float
    output: str


def _median(fn, reps):
    times = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t)
    return statistics.median(times)


class Benchmark:
    def __init__(self, program: A.Program, reps: int = 5, opt: str = "-O2") -> None:
        self.program, self.reps, self.opt = program, reps, opt

    def run(self) -> list[Result]:
        results = []

        # 1) Interprete de arbol: no hay preparacion
        buf: list = []
        def run_ast():
            buf.clear(); TreeInterpreter(self.program, buf.append).run()
        results.append(Result("Interprete AST", 0.0, _median(run_ast, self.reps),
                              " ".join(map(str, buf))))

        # 2) Bytecode + VM: preparacion = compilar a bytecode
        prep = _median(lambda: BytecodeCompiler(self.program).compile(), self.reps)
        compiled = BytecodeCompiler(self.program).compile()
        vbuf: list = []
        def run_vm():
            vbuf.clear(); VirtualMachine(compiled, vbuf.append).run()
        results.append(Result("Bytecode + VM", prep, _median(run_vm, self.reps),
                              " ".join(map(str, vbuf))))

        # 3) Nativo: preparacion = generar C + gcc; ejecucion = correr el .exe
        with tempfile.TemporaryDirectory() as d:
            t = time.perf_counter()
            exe = NativeBuilder(self.program, d, self.opt).build()
            prep = time.perf_counter() - t
            last = []
            def run_native():
                last[:] = [subprocess.run([exe], capture_output=True, text=True).stdout.strip()]
            e = _median(run_native, self.reps)
            results.append(Result(f"Nativo (C + GCC {self.opt})", prep, e, last[0]))
        return results

    @staticmethod
    def report(results: list[Result]) -> str:
        same = len({r.output for r in results}) == 1
        lines = [f"{'Implementacion':<26}{'Preparacion (s)':>17}{'Ejecucion (s)':>15}   Salida"]
        for r in results:
            lines.append(f"{r.name:<26}{r.prep_seconds:>17.4f}{r.exec_seconds:>15.4f}   {r.output}")
        lines.append("")
        lines.append("Resultados identicos en las 3 implementaciones." if same
                     else "ATENCION: las salidas NO coinciden.")
        lines.append("(El tiempo nativo incluye el arranque del proceso.)")
        return "\n".join(lines)
