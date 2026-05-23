# -*- coding: utf-8 -*-
"""
Amharic Programming Language (AML) — source-to-Python translator.
"""

from .lexer import Lexer, tokenize, format_token_stream
from .parser import Parser, parse
from .codegen import PythonGenerator, generate_python
from .errors import AmharicSyntaxError

__all__ = [
    "Lexer",
    "tokenize",
    "format_token_stream",
    "Parser",
    "parse",
    "PythonGenerator",
    "generate_python",
    "AmharicSyntaxError",
]
