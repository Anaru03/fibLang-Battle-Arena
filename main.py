#!/usr/bin/env python3
"""FibLang - linea de comandos.

  python3 main.py                (sin argumentos: abre la interfaz grafica)
  python3 main.py gui [--port 8765] [--no-browser]
  python3 main.py run   ejemplos/fib.fib --mode ast|vm|native
  python3 main.py dump  ejemplos/fib.fib          (tokens, AST, bytecode y C)
  python3 main.py trace ejemplos/fib.fib          (pila de la VM paso a paso)
  python3 main.py emit-c ejemplos/fib.fib -o fib.c
  python3 main.py bench ejemplos/fib27.fib --reps 5 --opt=-O2
"""
import argparse
import sys
import tempfile
import subprocess

sys.setrecursionlimit(100000)

from fiblang import (parse, Lexer, TreeInterpreter, BytecodeCompiler,
                     VirtualMachine, CGenerator, NativeBuilder, FibLangError)
from fiblang.ast_nodes import pretty
from fiblang.bytecode import disassemble
from fiblang.benchmark import Benchmark


def cmd_gui(a):
    from gui import serve
    serve(a.port, not a.no_browser)


def cmd_run(a):
    prog = parse(open(a.file, encoding="utf-8").read())
    if a.mode == "ast":
        TreeInterpreter(prog).run()
    elif a.mode == "vm":
        VirtualMachine(BytecodeCompiler(prog).compile()).run()
    else:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([NativeBuilder(prog, d, a.opt).build()])


def cmd_dump(a):
    src = open(a.file, encoding="utf-8").read()
    print("=== TOKENS ===");   print(Lexer(src).tokenize())
    prog = parse(src)
    print("\n=== AST ===");    print(pretty(prog))
    print("=== BYTECODE ==="); print(disassemble(BytecodeCompiler(prog).compile()))
    print("\n=== C GENERADO ==="); print(CGenerator(prog).generate())


def cmd_trace(a):
    prog = parse(open(a.file, encoding="utf-8").read())
    n = [0]
    def tr(ins, pc, stack):
        n[0] += 1
        if n[0] <= a.limit:
            print(f"pc={pc:03d}  {ins:<14} pila={stack}")
    VirtualMachine(BytecodeCompiler(prog).compile()).run(trace=tr)
    print(f"... total de instrucciones ejecutadas: {n[0]}")


def cmd_emit_c(a):
    prog = parse(open(a.file, encoding="utf-8").read())
    c = CGenerator(prog).generate()
    if a.o:
        open(a.o, "w", encoding="utf-8").write(c); print(f"Escrito {a.o}")
    else:
        print(c)


def cmd_bench(a):
    prog = parse(open(a.file, encoding="utf-8").read())
    print(Benchmark.report(Benchmark(prog, a.reps, a.opt).run()))


def main():
    if len(sys.argv) == 1:               # doble clic / sin argumentos -> interfaz
        sys.argv.append("gui")
    ap = argparse.ArgumentParser(description="FibLang")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("gui", help="abre la interfaz grafica en el navegador")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true"); p.set_defaults(fn=cmd_gui)
    p = sub.add_parser("run");  p.add_argument("file")
    p.add_argument("--mode", choices=["ast", "vm", "native"], default="ast")
    p.add_argument("--opt", default="-O2"); p.set_defaults(fn=cmd_run)
    p = sub.add_parser("dump"); p.add_argument("file"); p.set_defaults(fn=cmd_dump)
    p = sub.add_parser("trace"); p.add_argument("file")
    p.add_argument("--limit", type=int, default=60); p.set_defaults(fn=cmd_trace)
    p = sub.add_parser("emit-c"); p.add_argument("file"); p.add_argument("-o")
    p.set_defaults(fn=cmd_emit_c)
    p = sub.add_parser("bench"); p.add_argument("file")
    p.add_argument("--reps", type=int, default=5); p.add_argument("--opt", default="-O2")
    p.set_defaults(fn=cmd_bench)
    a = ap.parse_args()
    try:
        a.fn(a)
    except FibLangError as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)


if __name__ == "__main__":
    main()
