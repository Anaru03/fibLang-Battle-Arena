"""Analisis lexico: convierte texto en tokens."""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum, auto


class FibLangError(Exception):
    """Error del lenguaje (lexico, sintactico o semantico)."""


class TokenType(Enum):
    NUM = auto()
    ID = auto()
    KW = auto()
    OP = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int

    def __repr__(self) -> str:
        return f"{self.type.name}({self.value!r})"


class Lexer:
    KEYWORDS = {"fn", "if", "else", "return", "print", "let"}

    _PATTERN = re.compile(r"""
        (?P<WS>\s+|//[^\n]*)
      | (?P<NUM>\d+)
      | (?P<ID>[A-Za-z_]\w*)
      | (?P<OP>==|!=|<=|>=|[+\-*<>=(){};,])
    """, re.VERBOSE)

    def __init__(self, source: str) -> None:
        self.source = source

    def tokenize(self) -> list[Token]:
        pos, line, tokens = 0, 1, []
        while pos < len(self.source):
            m = self._PATTERN.match(self.source, pos)
            if not m:
                raise FibLangError(
                    f"Linea {line}: caracter inesperado {self.source[pos]!r}")
            pos = m.end()
            kind, text = m.lastgroup, m.group()
            if kind == "WS":
                line += text.count("\n")
                continue
            if kind == "NUM":
                tokens.append(Token(TokenType.NUM, text, line))
            elif kind == "ID":
                t = TokenType.KW if text in self.KEYWORDS else TokenType.ID
                tokens.append(Token(t, text, line))
            else:
                tokens.append(Token(TokenType.OP, text, line))
        tokens.append(Token(TokenType.EOF, "", line))
        return tokens
