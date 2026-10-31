"""FibLang: un lenguaje minimo con tres estrategias de ejecucion."""
from .tokens import FibLangError, Lexer, Token, TokenType
from .parser import Parser
from .interpreter import TreeInterpreter
from .bytecode import BytecodeCompiler
from .vm import VirtualMachine
from .cgen import CGenerator, NativeBuilder


def parse(source: str):
    """Frontend compartido: texto -> AST."""
    return Parser(Lexer(source).tokenize()).parse_program()
