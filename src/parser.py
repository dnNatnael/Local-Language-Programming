# -*- coding: utf-8 -*-
"""
Recursive descent parser for the Amharic Programming Language (AML).
"""

from typing import List, Optional

from . import ast_nodes as ast
from .errors import (
    AmharicSyntaxError,
    MSG_EXPECTED_ELSE_OR_END,
    MSG_EXPECTED_END,
    MSG_EXPECTED_EXPRESSION,
    MSG_EXPECTED_IDENTIFIER,
    MSG_EXPECTED_RPAREN,
    MSG_UNEXPECTED_TOKEN,
)
from .lexer import Token, TokenType


class Parser:
    """Builds an AST from a token stream using recursive descent."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ast.Program:
        statements = []
        self._skip_newlines()
        while not self._check(TokenType.EOF):
            statements.append(self._parse_statement())
            self._skip_newlines()
        return ast.Program(statements)

    # --- Token helpers ---

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek_ahead(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _check(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _advance(self) -> Token:
        if not self._at_end():
            self.pos += 1
        return self.tokens[self.pos - 1]

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _expect(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        tok = self._current()
        raise AmharicSyntaxError(message, tok.line, tok.column)

    def _match(self, *types: TokenType) -> bool:
        if self._check(*types):
            self._advance()
            return True
        return False

    # --- Statements ---

    def _parse_statement(self) -> ast.Statement:
        self._skip_newlines()
        tok = self._current()

        if self._check(TokenType.KW_NUMBER_TYPE, TokenType.KW_TEXT_TYPE):
            return self._parse_var_decl()
        if self._check(TokenType.KW_PRINT):
            return self._parse_print()
        if self._check(TokenType.KW_INPUT):
            return self._parse_input()
        if self._check(TokenType.KW_IF):
            return self._parse_if()
        if self._check(TokenType.KW_WHILE):
            return self._parse_while()
        if self._check(TokenType.KW_FUNCTION):
            return self._parse_function()
        if self._check(TokenType.KW_RETURN):
            return self._parse_return()
        if self._check(TokenType.IDENTIFIER) and self._peek_ahead().type == TokenType.EQ:
            return self._parse_assign()
        if self._check(TokenType.IDENTIFIER) and self._peek_ahead().type == TokenType.LPAREN:
            return ast.ExprStmt(self._parse_expression())

        if self._check(TokenType.KW_END, TokenType.KW_ELSE, TokenType.EOF):
            raise AmharicSyntaxError(
                MSG_UNEXPECTED_TOKEN.format(token=tok.value or tok.type.name),
                tok.line,
                tok.column,
            )

        return ast.ExprStmt(self._parse_expression())

    def _parse_var_decl(self) -> ast.VarDecl:
        type_tok = self._advance()
        var_type = type_tok.value
        name_tok = self._expect(TokenType.IDENTIFIER, MSG_EXPECTED_IDENTIFIER)
        self._expect(TokenType.EQ, "=' ተጠበቀ")
        value = self._parse_expression()
        return ast.VarDecl(var_type, name_tok.value, value)

    def _parse_assign(self) -> ast.Assign:
        name_tok = self._advance()
        self._expect(TokenType.EQ, "=' ተጠበቀ")
        value = self._parse_expression()
        return ast.Assign(name_tok.value, value)

    def _parse_print(self) -> ast.PrintStmt:
        self._advance()  # አትም
        expr = self._parse_expression()
        return ast.PrintStmt(expr)

    def _parse_input(self) -> ast.InputStmt:
        self._advance()  # ግቤት
        name_tok = self._expect(TokenType.IDENTIFIER, MSG_EXPECTED_IDENTIFIER)
        prompt = None
        if not self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.KW_END,
                          TokenType.KW_ELSE, TokenType.KW_RETURN):
            prompt = self._parse_expression()
        return ast.InputStmt(name_tok.value, prompt)

    def _parse_if(self) -> ast.IfStmt:
        self._advance()  # ከሆነ
        condition = self._parse_expression()
        self._skip_newlines()
        then_body = self._parse_block_until(TokenType.KW_ELSE, TokenType.KW_END)
        else_body = None
        if self._match(TokenType.KW_ELSE):
            self._skip_newlines()
            else_body = self._parse_block_until(TokenType.KW_END)
        self._expect(TokenType.KW_END, MSG_EXPECTED_END)
        return ast.IfStmt(condition, then_body, else_body)

    def _parse_while(self) -> ast.WhileStmt:
        self._advance()  # እስከ
        condition = self._parse_expression()
        self._skip_newlines()
        body = self._parse_block_until(TokenType.KW_END)
        self._expect(TokenType.KW_END, MSG_EXPECTED_END)
        return ast.WhileStmt(condition, body)

    def _parse_function(self) -> ast.FunctionDef:
        self._advance()  # ተግባር
        name_tok = self._expect(TokenType.IDENTIFIER, MSG_EXPECTED_IDENTIFIER)
        self._expect(TokenType.LPAREN, "'(' ተጠበቀ")
        params = self._parse_param_list()
        self._expect(TokenType.RPAREN, MSG_EXPECTED_RPAREN)
        self._skip_newlines()
        body = self._parse_block_until(TokenType.KW_END)
        self._expect(TokenType.KW_END, MSG_EXPECTED_END)
        return ast.FunctionDef(name_tok.value, params, body)

    def _parse_param_list(self) -> List[str]:
        params = []
        if self._check(TokenType.RPAREN):
            return params
        while True:
            param = self._expect(TokenType.IDENTIFIER, MSG_EXPECTED_IDENTIFIER)
            params.append(param.value)
            if not self._match(TokenType.COMMA):
                break
        return params

    def _parse_return(self) -> ast.ReturnStmt:
        self._advance()  # መልስ
        if self._check(TokenType.NEWLINE, TokenType.EOF, TokenType.KW_END,
                      TokenType.KW_ELSE):
            return ast.ReturnStmt(None)
        value = self._parse_expression()
        return ast.ReturnStmt(value)

    def _parse_block_until(self, *stop_types: TokenType) -> List[ast.Statement]:
        """Parse statements until a stop token (not consumed)."""
        body = []
        self._skip_newlines()
        while not self._check(*stop_types, TokenType.EOF):
            body.append(self._parse_statement())
            self._skip_newlines()
        return body

    # --- Expressions (precedence climbing via recursive descent) ---

    def _parse_expression(self) -> ast.Expression:
        return self._parse_or()

    def _parse_or(self) -> ast.Expression:
        left = self._parse_and()
        while self._match(TokenType.KW_OR):
            right = self._parse_and()
            left = ast.BinaryOp(left, "||", right)
        return left

    def _parse_and(self) -> ast.Expression:
        left = self._parse_equality()
        while self._match(TokenType.KW_AND):
            right = self._parse_equality()
            left = ast.BinaryOp(left, "&&", right)
        return left

    def _parse_equality(self) -> ast.Expression:
        left = self._parse_comparison()
        while self._match(TokenType.EQEQ):
            right = self._parse_comparison()
            left = ast.BinaryOp(left, "==", right)
        return left

    def _parse_comparison(self) -> ast.Expression:
        left = self._parse_additive()
        while True:
            if self._match(TokenType.LT):
                right = self._parse_additive()
                left = ast.BinaryOp(left, "<", right)
            elif self._match(TokenType.GT):
                right = self._parse_additive()
                left = ast.BinaryOp(left, ">", right)
            else:
                break
        return left

    def _parse_additive(self) -> ast.Expression:
        left = self._parse_multiplicative()
        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_multiplicative()
                left = ast.BinaryOp(left, "+", right)
            elif self._match(TokenType.MINUS):
                right = self._parse_multiplicative()
                left = ast.BinaryOp(left, "-", right)
            else:
                break
        return left

    def _parse_multiplicative(self) -> ast.Expression:
        left = self._parse_unary()
        while True:
            if self._match(TokenType.STAR):
                right = self._parse_unary()
                left = ast.BinaryOp(left, "*", right)
            elif self._match(TokenType.SLASH):
                right = self._parse_unary()
                left = ast.BinaryOp(left, "/", right)
            else:
                break
        return left

    def _parse_unary(self) -> ast.Expression:
        if self._match(TokenType.KW_NOT):
            operand = self._parse_unary()
            return ast.UnaryOp("!", operand)
        if self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return ast.UnaryOp("-", operand)
        return self._parse_primary()

    def _parse_primary(self) -> ast.Expression:
        tok = self._current()

        if self._match(TokenType.NUMBER):
            val = float(tok.value)
            if val == int(val):
                return ast.NumberLiteral(int(val))
            return ast.NumberLiteral(val)

        if self._match(TokenType.STRING):
            return ast.StringLiteral(tok.value)

        if self._match(TokenType.KW_TRUE):
            return ast.BoolLiteral(True)

        if self._match(TokenType.KW_FALSE):
            return ast.BoolLiteral(False)

        if self._match(TokenType.IDENTIFIER):
            name = tok.value
            if self._match(TokenType.LPAREN):
                args = self._parse_argument_list()
                self._expect(TokenType.RPAREN, MSG_EXPECTED_RPAREN)
                return ast.CallExpr(name, args)
            return ast.Identifier(name)

        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, MSG_EXPECTED_RPAREN)
            return expr

        raise AmharicSyntaxError(MSG_EXPECTED_EXPRESSION, tok.line, tok.column)

    def _parse_argument_list(self) -> List[ast.Expression]:
        args = []
        if self._check(TokenType.RPAREN):
            return args
        while True:
            args.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        return args


def parse(tokens: List[Token]) -> ast.Program:
    """Convenience parse function."""
    return Parser(tokens).parse()
