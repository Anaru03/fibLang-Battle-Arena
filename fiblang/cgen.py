"""COMPETIDOR 3: generador de C + compilacion nativa con GCC.

Nota: en C los enteros son 'long' de 64 bits; en Python y en la VM son
enteros de precision arbitraria. Para comparar, usa valores que no desborden.
"""
from __future__ import annotations
import os
import shutil
import subprocess
from . import ast_nodes as A
from .tokens import FibLangError


class CGenerator:
    def __init__(self, program: A.Program) -> None:
        self.program = program

    def generate(self) -> str:
        p = self.program
        L = ["#include <stdio.h>", ""]
        for f in p.functions:
            L.append(self._signature(f) + ";")
        L.append("")
        for f in p.functions:
            L.append(self._signature(f) + " {")
            L += self._declare_locals(f.body, set(f.params))
            L += self._stmts(f.body, 1)
            L += ["    return 0;", "}", ""]
        L.append("int main(void) {")
        L += self._declare_locals(p.main, set())
        L += self._stmts(p.main, 1)
        L += ["    return 0;", "}"]
        return "\n".join(L) + "\n"

    # nombres con prefijo para no chocar con palabras reservadas de C
    @staticmethod
    def _fn(n): return f"fl_{n}"
    @staticmethod
    def _v(n): return f"v_{n}"

    def _signature(self, f: A.Function) -> str:
        params = ", ".join(f"long {self._v(p)}" for p in f.params) or "void"
        return f"long {self._fn(f.name)}({params})"

    def _declare_locals(self, body, params) -> list[str]:
        names: list[str] = []
        def walk(stmts):
            for s in stmts:
                if isinstance(s, A.Let) and s.name not in params and s.name not in names:
                    names.append(s.name)
                elif isinstance(s, A.If):
                    walk(s.then); walk(s.orelse)
        walk(body)
        return [f"    long {self._v(n)} = 0;" for n in names]

    def _expr(self, e) -> str:
        if isinstance(e, A.Num): return f"{e.value}L"
        if isinstance(e, A.Var): return self._v(e.name)
        if isinstance(e, A.BinOp): return f"({self._expr(e.left)} {e.op} {self._expr(e.right)})"
        if isinstance(e, A.Call):
            return f"{self._fn(e.name)}({', '.join(self._expr(a) for a in e.args)})"
        raise FibLangError(f"Expresion no soportada: {e}")

    def _stmts(self, stmts, ind) -> list[str]:
        pad, out = "    " * ind, []
        for s in stmts:
            if isinstance(s, (A.Let, A.Assign)):
                out.append(f"{pad}{self._v(s.name)} = {self._expr(s.expr)};")
            elif isinstance(s, A.Print):
                out.append(f'{pad}printf("%ld\\n", (long)({self._expr(s.expr)}));')
            elif isinstance(s, A.Return):
                out.append(f"{pad}return {self._expr(s.expr)};")
            elif isinstance(s, A.If):
                out.append(f"{pad}if ({self._expr(s.cond)}) {{")
                out += self._stmts(s.then, ind + 1)
                if s.orelse:
                    out.append(f"{pad}}} else {{")
                    out += self._stmts(s.orelse, ind + 1)
                out.append(f"{pad}}}")
        return out


class NativeBuilder:
    """Escribe el .c, llama a gcc y devuelve la ruta del ejecutable."""

    def __init__(self, program: A.Program, workdir: str, opt: str = "-O2") -> None:
        self.program, self.workdir, self.opt = program, workdir, opt

    def build(self) -> str:
        gcc = shutil.which("gcc")
        if gcc is None:
            raise FibLangError("No se encontro 'gcc'. Instalalo (Linux: build-essential, "
                               "macOS: xcode-select --install, Windows: MinGW/MSYS2).")
        c_path = os.path.join(self.workdir, "fiblang_out.c")
        exe = os.path.join(self.workdir, "fiblang_out" + (".exe" if os.name == "nt" else ""))
        with open(c_path, "w", encoding="utf-8") as f:
            f.write(CGenerator(self.program).generate())
        subprocess.run([gcc, self.opt, c_path, "-o", exe], check=True)
        return exe
