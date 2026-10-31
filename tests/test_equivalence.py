"""Las tres estrategias deben producir exactamente el mismo resultado."""
import os, shutil, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.setrecursionlimit(100000)

from fiblang import parse, TreeInterpreter, BytecodeCompiler, VirtualMachine, NativeBuilder, FibLangError

FIB = "fn fib(n){ if (n < 2) { return n; } return fib(n-1)+fib(n-2); }\n"
CASES = {
    "fib0": FIB + "print(fib(0));",
    "fib1": FIB + "print(fib(1));",
    "fib10": FIB + "print(fib(10));",
    "fib20": FIB + "print(fib(20));",
    "vars": "let a = 4; let b = a * 5 - 3; a = a + b; print(a); print(b);",
    "ifelse": "fn f(x){ if (x == 3) { return 100; } else { return 200; } } print(f(3)); print(f(4));",
    "multi": "fn add(a,b){ return a+b; } fn dbl(x){ return add(x,x); } print(dbl(21));",
}


def run_ast(src):
    out = []; TreeInterpreter(parse(src), out.append).run(); return out

def run_vm(src):
    out = []; VirtualMachine(BytecodeCompiler(parse(src)).compile(), out.append).run(); return out

def run_native(src):
    with tempfile.TemporaryDirectory() as d:
        exe = NativeBuilder(parse(src), d).build()
        r = subprocess.run([exe], capture_output=True, text=True)
        return [int(x) for x in r.stdout.split()]


class Equivalence(unittest.TestCase):
    def test_ast_vs_vm(self):
        for name, src in CASES.items():
            with self.subTest(name):
                self.assertEqual(run_ast(src), run_vm(src))

    @unittest.skipIf(shutil.which("gcc") is None, "gcc no disponible")
    def test_native_matches(self):
        for name, src in CASES.items():
            with self.subTest(name):
                self.assertEqual(run_ast(src), run_native(src))

    def test_fib10_is_55(self):
        self.assertEqual(run_ast(FIB + "print(fib(10));"), [55])

    def test_errors(self):
        with self.assertRaises(FibLangError):
            run_ast("print(x);")
        with self.assertRaises(FibLangError):
            parse("print(1")


if __name__ == "__main__":
    unittest.main()
