# -*- coding: utf-8 -*-
"""Basic tests for AML lexer, parser, and codegen."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lexer import tokenize, TokenType
from src.parser import parse
from src.codegen import generate_python


def test_variables_translate():
    source = """ቁጥር x = 10
ቁጥር y = 20
አትም x + y
"""
    tokens = tokenize(source)
    assert any(t.type == TokenType.KW_NUMBER_TYPE for t in tokens)
    program = parse(tokens)
    py = generate_python(program)
    assert "x = 10" in py
    assert "print (" in py


def test_function_translate():
    source = """ተግባር ድምር(a, b)
መልስ a + b
መጨረሻ
"""
    program = parse(tokenize(source))
    py = generate_python(program)
    assert "def ድምር" in py
    assert "return" in py


def test_if_requires_end():
    source = """ከሆነ x > 5
አትም 1
"""
    try:
        parse(tokenize(source))
        assert False, "Should raise"
    except Exception as e:
        assert "መጨረሻ" in str(e)


if __name__ == "__main__":
    test_variables_translate()
    test_function_translate()
    test_if_requires_end()
    print("All tests passed.")
