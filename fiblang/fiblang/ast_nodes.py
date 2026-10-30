"""Nodos del arbol sintactico abstracto (AST)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


# ----- Expresiones
@dataclass
class Num:
    value: int


@dataclass
class Var:
    name: str


@dataclass
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass
class Call:
    name: str
    args: list["Expr"]


Expr = Union[Num, Var, BinOp, Call]


# ----- Sentencias
@dataclass
class Let:
    name: str
    expr: Expr


@dataclass
class Assign:
    name: str
    expr: Expr


@dataclass
class If:
    cond: Expr
    then: list["Stmt"]
    orelse: list["Stmt"]


@dataclass
class Return:
    expr: Expr


@dataclass
class Print:
    expr: Expr


Stmt = Union[Let, Assign, If, Return, Print]


# ----- Estructura del programa
@dataclass
class Function:
    name: str
    params: list[str]
    body: list[Stmt]


@dataclass
class Program:
    functions: list[Function] = field(default_factory=list)
    main: list[Stmt] = field(default_factory=list)


def pretty(node, indent: int = 0) -> str:
    """Imprime el AST con sangria (util para mostrarlo en el video)."""
    pad = "  " * indent
    if isinstance(node, list):
        return "".join(pretty(n, indent) for n in node)
    if isinstance(node, Program):
        return pretty(node.functions, indent) + pad + "main:\n" + pretty(node.main, indent + 1)
    if isinstance(node, Function):
        return f"{pad}fn {node.name}({', '.join(node.params)})\n" + pretty(node.body, indent + 1)
    if isinstance(node, If):
        s = f"{pad}If\n{pad}  cond:\n{pretty(node.cond, indent + 2)}{pad}  then:\n{pretty(node.then, indent + 2)}"
        if node.orelse:
            s += f"{pad}  else:\n{pretty(node.orelse, indent + 2)}"
        return s
    if isinstance(node, Num):
        return f"{pad}Num({node.value})\n"
    if isinstance(node, Var):
        return f"{pad}Var({node.name})\n"
    if isinstance(node, BinOp):
        return f"{pad}BinOp({node.op})\n" + pretty(node.left, indent + 1) + pretty(node.right, indent + 1)
    if isinstance(node, Call):
        return f"{pad}Call({node.name})\n" + pretty(node.args, indent + 1)
    if isinstance(node, (Let, Assign)):
        return f"{pad}{type(node).__name__}({node.name})\n" + pretty(node.expr, indent + 1)
    if isinstance(node, (Return, Print)):
        return f"{pad}{type(node).__name__}\n" + pretty(node.expr, indent + 1)
    raise TypeError(node)
