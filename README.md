# FibLang

Lenguaje minimo para demostrar tres estrategias de ejecucion del mismo programa:

| Competidor | Archivo | Idea |
|---|---|---|
| 1. Interprete de arbol | `fiblang/interpreter.py` | Recorre el AST y evalua |
| 2. Bytecode + VM | `fiblang/bytecode.py`, `fiblang/vm.py` | AST -> instrucciones -> maquina de pila |
| 3. Nativo | `fiblang/cgen.py` | AST -> C -> GCC -> ejecutable |

Interfaz: `gui.py` (servidor local) y `web/index.html`.

Frontend compartido: `tokens.py` (lexer), `ast_nodes.py`, `parser.py`.

## Requisitos
- Python 3.9+ (sin librerias externas)
- GCC (solo para el modo nativo): Linux `sudo apt install build-essential`,
  macOS `xcode-select --install`, Windows MSYS2/MinGW.

## Inicio rapido (interfaz grafica)
```
python3 main.py          # abre el navegador con la carrera
```
Tambien: doble clic en `iniciar.bat` (Windows) o `./iniciar.sh` (Linux/macOS).
La interfaz corre el interprete de arbol, la VM de bytecode y un compilador a
JavaScript en el navegador, y pide a Python que compile con GCC y mida el
carril nativo real. Opciones: `python3 main.py gui --port 9000 --no-browser`.

## Uso en consola
```
python3 main.py run    ejemplos/fib.fib --mode ast
python3 main.py run    ejemplos/fib.fib --mode vm
python3 main.py run    ejemplos/fib.fib --mode native
python3 main.py dump   ejemplos/fib.fib        # tokens, AST, bytecode, C
python3 main.py trace  ejemplos/fib.fib        # pila de la VM paso a paso
python3 main.py emit-c ejemplos/fib.fib -o fib.c
python3 main.py bench  ejemplos/fib30.fib --reps 5 --opt=-O2
python3 -m unittest discover tests -v
```
Prueba tambien `--opt=-O0` para ver como cambia el resultado nativo.

## El lenguaje
```
fn fib(n) {
    if (n < 2) { return n; }
    return fib(n - 1) + fib(n - 2);
}
let x = 10;
print(fib(x));
```
Enteros, `+ - *`, comparaciones, `let`, asignacion, `if/else`, funciones, `return`, `print`.
