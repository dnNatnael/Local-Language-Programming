# -*- coding: utf-8 -*-
"""
Unicode-aware lexer for the Amharic Programming Language (AML).

Tokenizes source files containing Amharic keywords, Unicode identifiers,
numbers, strings, and operators.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List

from .errors import AmharicSyntaxError, MSG_INVALID_NUMBER, MSG_UNTERMINATED_STRING


class TokenType(Enum):
    # Amharic keywords
    KW_PRINT = auto()       # አትም
    KW_INPUT = auto()       # ግቤት
    KW_IF = auto()          # ከሆነ
    KW_ELSE = auto()        # ካልሆነ
    KW_WHILE = auto()       # እስከ
    KW_FUNCTION = auto()    # ተግባር
    KW_RETURN = auto()      # መልስ
    KW_END = auto()         # መጨረሻ
    KW_TRUE = auto()        # እውነት
    KW_FALSE = auto()       # ሐሰት
    KW_NUMBER_TYPE = auto() # ቁጥር
    KW_TEXT_TYPE = auto()   # ጽሑፍ
    KW_AND = auto()         # እና
    KW_OR = auto()          # ወይም
    KW_NOT = auto()         # አይደለም

    # Literals and identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Operators and punctuation
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()             # =
    EQEQ = auto()           # ==
    LT = auto()
    GT = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()

    # Structure
    NEWLINE = auto()
    EOF = auto()


# Map Amharic keyword strings to token types
KEYWORDS = {
    "አትም": TokenType.KW_PRINT,
    "ግቤት": TokenType.KW_INPUT,
    "ከሆነ": TokenType.KW_IF,
    "ካልሆነ": TokenType.KW_ELSE,
    "እስከ": TokenType.KW_WHILE,
    "ተግባር": TokenType.KW_FUNCTION,
    "መልስ": TokenType.KW_RETURN,
    "መጨረሻ": TokenType.KW_END,
    "እውነት": TokenType.KW_TRUE,
    "ሐሰት": TokenType.KW_FALSE,
    "ቁጥር": TokenType.KW_NUMBER_TYPE,
    "ጽሑፍ": TokenType.KW_TEXT_TYPE,
    "እና": TokenType.KW_AND,
    "ወይም": TokenType.KW_OR,
    "አይደለም": TokenType.KW_NOT,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    """Unicode-aware tokenizer for AML source code."""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Scan entire source and return token list."""
        while not self._at_end():
            self._skip_whitespace_and_comments()
            if self._at_end():
                break
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def _at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx >= len(self.source):
            return "\0"
        return self.source[idx]

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _add_token(self, token_type: TokenType, value: str = ""):
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def _skip_whitespace_and_comments(self):
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
            elif ch == "#":
                # Comment until end of line
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
            else:
                break

    def _scan_token(self):
        start_line = self.line
        start_col = self.column
        ch = self._peek()

        # Newline
        if ch == "\n":
            self._advance()
            # Collapse consecutive newlines; avoid duplicate NEWLINE tokens
            if self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
                return
            self.tokens.append(Token(TokenType.NEWLINE, "\\n", start_line, start_col))
            return

        # Single-character tokens
        single_char = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ",": TokenType.COMMA,
        }
        if ch in single_char:
            self._advance()
            self.tokens.append(Token(single_char[ch], ch, start_line, start_col))
            return

        # = and ==
        if ch == "=":
            self._advance()
            if self._peek() == "=":
                self._advance()
                self.tokens.append(Token(TokenType.EQEQ, "==", start_line, start_col))
            else:
                self.tokens.append(Token(TokenType.EQ, "=", start_line, start_col))
            return

        # String literal
        if ch in '"\'':
            self._scan_string(ch)
            return

        # Number
        if ch.isdigit() or (ch == "." and self._peek(1).isdigit()):
            self._scan_number(start_line, start_col)
            return

        # Identifier or keyword (Unicode letters)
        if self._is_identifier_start(ch):
            self._scan_identifier_or_keyword(start_line, start_col)
            return

        raise AmharicSyntaxError(
            f"ያልታወቀ ቁምፊ '{ch}'",
            start_line,
            start_col,
        )

    def _scan_string(self, quote: str):
        start_line = self.line
        start_col = self.column
        self._advance()  # opening quote
        chars = []
        while not self._at_end() and self._peek() != quote:
            if self._peek() == "\\":
                self._advance()
                if self._at_end():
                    break
                esc = self._advance()
                escape_map = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'"}
                chars.append(escape_map.get(esc, esc))
            elif self._peek() == "\n":
                raise AmharicSyntaxError(MSG_UNTERMINATED_STRING, start_line, start_col)
            else:
                chars.append(self._advance())
        if self._at_end():
            raise AmharicSyntaxError(MSG_UNTERMINATED_STRING, start_line, start_col)
        self._advance()  # closing quote
        self.tokens.append(
            Token(TokenType.STRING, "".join(chars), start_line, start_col)
        )

    def _scan_number(self, start_line: int, start_col: int):
        num_str = ""
        while self._peek().isdigit():
            num_str += self._advance()
        if self._peek() == "." and self._peek(1).isdigit():
            num_str += self._advance()
            while self._peek().isdigit():
                num_str += self._advance()
        try:
            float(num_str)
        except ValueError:
            raise AmharicSyntaxError(MSG_INVALID_NUMBER, start_line, start_col)
        self.tokens.append(Token(TokenType.NUMBER, num_str, start_line, start_col))

    def _scan_identifier_or_keyword(self, start_line: int, start_col: int):
        text = ""
        while self._is_identifier_part(self._peek()):
            text += self._advance()
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, text, start_line, start_col))

    @staticmethod
    def _is_identifier_start(ch: str) -> bool:
        if ch == "\0":
            return False
        # Unicode letter categories + underscore
        return ch == "_" or ch.isalpha()

    @staticmethod
    def _is_identifier_part(ch: str) -> bool:
        if ch == "\0":
            return False
        return ch == "_" or ch.isalnum()


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source."""
    return Lexer(source).tokenize()


def format_token_stream(tokens: List[Token]) -> str:
    """Format tokens for debugging / documentation."""
    lines = []
    for t in tokens:
        if t.type == TokenType.EOF:
            lines.append("EOF")
            break
        lines.append(f"{t.type.name:20} {repr(t.value):15} @ {t.line}:{t.column}")
    return "\n".join(lines)
