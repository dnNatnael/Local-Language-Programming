#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AML (Amharic Programming Language) — Command-line translator.

Usage:
    python translator.py program.aml
    python translator.py program.aml -o output.py
    python translator.py program.aml --tokens   # debug: show token stream
    python translator.py program.aml --ast      # debug: show AST (simplified)
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.lexer import Lexer, format_token_stream
from src.parser import Parser
from src.codegen import generate_python
from src.errors import AmharicSyntaxError


def translate(source: str, show_tokens: bool = False) -> str:
    """Lex, parse, and generate Python from AML source."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    if show_tokens:
        print("=== Token Stream ===")
        print(format_token_stream(tokens))
        print()

    parser = Parser(tokens)
    program = parser.parse()
    return generate_python(program)


def _configure_stdout_encoding():
    """Avoid Windows console UnicodeEncodeError on Amharic messages."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def main():
    _configure_stdout_encoding()
    parser = argparse.ArgumentParser(
        description="አማርኛ ፕሮግራሚንግ ቋንቋ (AML) → Python ተርጓሚ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ምሳሌ:
  python translator.py examples/01_variables.aml
  python translator.py program.aml -o program.py
        """,
    )
    parser.add_argument(
        "input",
        help="AML ምንጭ ፋይል (.aml)",
    )
    parser.add_argument(
        "-o", "--output",
        help="የወጣ Python ፋይል (ነባሪ: የግብት ስም.py)",
    )
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="የምልክቶች ዝርዝር አሳይ (ለማረም)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ስህተት: ፋይሉ '{input_path}' አልተገኘም", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".py")

    try:
        source = input_path.read_text(encoding="utf-8")
        py_code = translate(source, show_tokens=args.tokens)
        output_path.write_text(py_code, encoding="utf-8")
        print(f"ተተርጉሟል: {input_path} → {output_path}")
    except AmharicSyntaxError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ስህተት: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
