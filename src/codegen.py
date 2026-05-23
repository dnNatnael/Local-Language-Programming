# -*- coding: utf-8 -*-
"""
Python code generator — translates AML AST to executable Python.
"""

import json
from typing import List

from . import ast_nodes as ast

# Map JS-style operators from the parser to Python
_BINARY_OP_MAP = {
    "||": "or",
    "&&": "and",
}


class PythonGenerator:
    """Walks the AST and emits formatted Python."""

    def __init__(self, indent: str = "    "):
        self.indent_str = indent
        self.lines: List[str] = []
        self.indent_level = 0

    def generate(self, program: ast.Program) -> str:
        self.lines = []
        self.indent_level = 0
        for stmt in program.statements:
            self._emit_statement(stmt)
        return "\n".join(self.lines) + "\n"

    def _write(self, line: str = ""):
        if line:
            self.lines.append(self.indent_str * self.indent_level + line)
        else:
            self.lines.append("")

    def _indent(self):
        self.indent_level += 1

    def _dedent(self):
        self.indent_level -= 1

    # --- Statements ---

    def _emit_statement(self, stmt: ast.Statement):
        if isinstance(stmt, ast.VarDecl):
            self._emit_var_decl(stmt)
        elif isinstance(stmt, ast.Assign):
            self._write(f"{stmt.name} = {self._emit_expression(stmt.value)}")
        elif isinstance(stmt, ast.PrintStmt):
            self._write(f"print ({self._emit_expression(stmt.expression)})")
        elif isinstance(stmt, ast.InputStmt):
            self._emit_input(stmt)
        elif isinstance(stmt, ast.IfStmt):
            self._emit_if(stmt)
        elif isinstance(stmt, ast.WhileStmt):
            self._emit_while(stmt)
        elif isinstance(stmt, ast.FunctionDef):
            self._emit_function(stmt)
        elif isinstance(stmt, ast.ReturnStmt):
            if stmt.value is None:
                self._write("return")
            else:
                self._write(f"return {self._emit_expression(stmt.value)}")
        elif isinstance(stmt, ast.ExprStmt):
            self._write(self._emit_expression(stmt.expression))

    def _emit_var_decl(self, stmt: ast.VarDecl):
        if stmt.initializer is not None:
            self._write(
                f"{stmt.name} = {self._emit_expression(stmt.initializer)}"
            )
        else:
            self._write(f"{stmt.name} = None")

    def _emit_input(self, stmt: ast.InputStmt):
        if stmt.prompt:
            prompt = self._emit_expression(stmt.prompt)
            self._write(f"{stmt.name} = input({prompt})")
        else:
            self._write(f'{stmt.name} = input("ግቤት: ")')

    def _emit_if(self, stmt: ast.IfStmt):
        cond = self._emit_expression(stmt.condition)
        self._write(f"if {cond}:")
        self._indent()
        for s in stmt.then_body:
            self._emit_statement(s)
        self._dedent()
        if stmt.else_body:
            self._write("else:")
            self._indent()
            for s in stmt.else_body:
                self._emit_statement(s)
            self._dedent()

    def _emit_while(self, stmt: ast.WhileStmt):
        cond = self._emit_expression(stmt.condition)
        self._write(f"while {cond}:")
        self._indent()
        for s in stmt.body:
            self._emit_statement(s)
        self._dedent()

    def _emit_function(self, stmt: ast.FunctionDef):
        params = ", ".join(stmt.parameters)
        self._write(f"def {stmt.name}({params}):")
        self._indent()
        for s in stmt.body:
            self._emit_statement(s)
        self._dedent()

    # --- Expressions ---

    def _emit_expression(self, expr: ast.Expression) -> str:
        if isinstance(expr, ast.NumberLiteral):
            if isinstance(expr.value, int):
                return str(expr.value)
            return str(expr.value)

        if isinstance(expr, ast.StringLiteral):
            return json.dumps(expr.value, ensure_ascii=False)

        if isinstance(expr, ast.BoolLiteral):
            return "True" if expr.value else "False"

        if isinstance(expr, ast.Identifier):
            return expr.name

        if isinstance(expr, ast.BinaryOp):
            left = self._emit_expression(expr.left)
            right = self._emit_expression(expr.right)
            op = _BINARY_OP_MAP.get(expr.operator, expr.operator)
            return f"{left} {op} {right}"

        if isinstance(expr, ast.UnaryOp):
            operand = self._emit_expression(expr.operand)
            if expr.operator == "!":
                return f"not {operand}"
            return f"-{operand}"

        if isinstance(expr, ast.CallExpr):
            args = ", ".join(self._emit_expression(a) for a in expr.arguments)
            return f"{expr.callee}({args})"

        return "None"


def generate_python(program: ast.Program) -> str:
    """Generate Python source from an AML program AST."""
    return PythonGenerator().generate(program)
