"""Analisis sintactico: tokens -> AST (descenso recursivo).

Gramatica:
  programa  := (funcion | sentencia)*
  funcion   := 'fn' ID '(' [ID (',' ID)*] ')' bloque
  bloque    := '{' sentencia* '}'
  sentencia := 'let' ID '=' expr ';' | ID '=' expr ';'
             | 'if' '(' expr ')' bloque ['else' bloque]
             | 'return' expr ';' | 'print' '(' expr ')' ';'
  expr      := suma (('<'|'>'|'=='|'!='|'<='|'>=') suma)*
  suma      := mult (('+'|'-') mult)*
  mult      := prim ('*' prim)*
  prim      := NUM | ID | ID '(' [expr (',' expr)*] ')' | '(' expr ')'
"""
from __future__ import annotations
from .tokens import FibLangError, Token, TokenType
from . import ast_nodes as A

COMPARISONS = ("<", ">", "==", "!=", "<=", ">=")


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    # ---- utilidades
    def _peek(self, offset: int = 0) -> Token:
        return self.tokens[min(self.i + offset, len(self.tokens) - 1)]

    def _next(self) -> Token:
        tok = self._peek()
        self.i += 1
        return tok

    def _check(self, value: str) -> bool:
        t = self._peek()
        return t.type in (TokenType.OP, TokenType.KW) and t.value == value

    def _accept(self, value: str) -> bool:
        if self._check(value):
            self.i += 1
            return True
        return False

    def _expect(self, value: str) -> Token:
        if not self._check(value):
            t = self._peek()
            raise FibLangError(
                f"Linea {t.line}: se esperaba {value!r} y llego {t.value or 'fin de archivo'!r}")
        return self._next()

    def _ident(self) -> str:
        t = self._next()
        if t.type is not TokenType.ID:
            raise FibLangError(f"Linea {t.line}: se esperaba un identificador")
        return t.value

    # ---- reglas
    def parse_program(self) -> A.Program:
        prog = A.Program()
        while self._peek().type is not TokenType.EOF:
            if self._check("fn"):
                prog.functions.append(self._function())
            else:
                prog.main.append(self._statement())
        return prog

    def _function(self) -> A.Function:
        self._expect("fn")
        name = self._ident()
        self._expect("(")
        params: list[str] = []
        if not self._accept(")"):
            params.append(self._ident())
            while self._accept(","):
                params.append(self._ident())
            self._expect(")")
        return A.Function(name, params, self._block())

    def _block(self) -> list:
        self._expect("{")
        stmts = []
        while not self._accept("}"):
            if self._peek().type is TokenType.EOF:
                raise FibLangError("Falta '}' al final del archivo")
            stmts.append(self._statement())
        return stmts

    def _statement(self):
        t = self._peek()
        if self._accept("let"):
            name = self._ident()
            self._expect("=")
            e = self._expr()
            self._expect(";")
            return A.Let(name, e)
        if self._accept("if"):
            self._expect("(")
            cond = self._expr()
            self._expect(")")
            then = self._block()
            orelse = self._block() if self._accept("else") else []
            return A.If(cond, then, orelse)
        if self._accept("return"):
            e = self._expr()
            self._expect(";")
            return A.Return(e)
        if self._accept("print"):
            self._expect("(")
            e = self._expr()
            self._expect(")")
            self._expect(";")
            return A.Print(e)
        if t.type is TokenType.ID and self._peek(1).value == "=":
            name = self._ident()
            self._expect("=")
            e = self._expr()
            self._expect(";")
            return A.Assign(name, e)
        raise FibLangError(f"Linea {t.line}: sentencia invalida en {t.value!r}")

    def _expr(self):
        left = self._add()
        while self._peek().type is TokenType.OP and self._peek().value in COMPARISONS:
            op = self._next().value
            left = A.BinOp(op, left, self._add())
        return left

    def _add(self):
        left = self._mul()
        while self._peek().type is TokenType.OP and self._peek().value in ("+", "-"):
            op = self._next().value
            left = A.BinOp(op, left, self._mul())
        return left

    def _mul(self):
        left = self._primary()
        while self._accept("*"):
            left = A.BinOp("*", left, self._primary())
        return left

    def _primary(self):
        t = self._next()
        if t.type is TokenType.NUM:
            return A.Num(int(t.value))
        if t.type is TokenType.OP and t.value == "(":
            e = self._expr()
            self._expect(")")
            return e
        if t.type is TokenType.ID:
            if self._accept("("):
                args = []
                if not self._accept(")"):
                    args.append(self._expr())
                    while self._accept(","):
                        args.append(self._expr())
                    self._expect(")")
                return A.Call(t.value, args)
            return A.Var(t.value)
        raise FibLangError(f"Linea {t.line}: expresion invalida en {t.value!r}")
