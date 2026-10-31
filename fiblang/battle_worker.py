import json
import sys
from . import parse
from .benchmark import Benchmark


def main():
    n = int(sys.argv[1])
    if not 2 <= n <= 20:
        raise ValueError('El reto debe estar entre 2 y 20')
    source = ('fn fib(n) { if (n < 2) { return n; } '
              'return fib(n - 1) + fib(n - 2); }\n'
              f'print(fib({n}));\n')
    results = Benchmark(parse(source), reps=3, opt='-O2').run()
    outputs = [r.output.strip() for r in results]
    if len(set(outputs)) != 1:
        raise ValueError('Las tres implementaciones no coinciden')
    print(json.dumps({'n': n, 'result': outputs[0], 'results': [
        {'key': key, 'name': r.name, 'prep_ms': r.prep_seconds * 1000,
         'exec_ms': r.exec_seconds * 1000, 'output': r.output}
        for key, r in zip(('ast', 'vm', 'native'), results)
    ]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
