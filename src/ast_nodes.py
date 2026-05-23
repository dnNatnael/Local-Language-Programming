# -*- coding: utf-8 -*-
"""
Abstract Syntax Tree node definitions for the Amharic Programming Language (AML).
"""

from dataclasses import dataclass
from typing import List, Optional, Union


# --- Expressions ---

@dataclass
class NumberLiteral:
    value: float


@dataclass
class StringLiteral:
    value: str


@dataclass
class BoolLiteral:
    value: bool


@dataclass
class Identifier:
    name: str


@dataclass
class BinaryOp:
    left: "Expression"
    operator: str  # +, -, *, /, ==, <, >
    right: "Expression"


@dataclass
class UnaryOp:
    operator: str  # አይደለም (not) as unary minus if needed
    operand: "Expression"


@dataclass
class CallExpr:
    callee: str
    arguments: List["Expression"]


Expression = Union[
    NumberLiteral,
    StringLiteral,
    BoolLiteral,
    Identifier,
    BinaryOp,
    UnaryOp,
    CallExpr,
]


# --- Statements ---

@dataclass
class VarDecl:
    var_type: str  # "ቁጥር" or "ጽሑፍ"
    name: str
    initializer: Optional[Expression]


@dataclass
class Assign:
    name: str
    value: Expression


@dataclass
class PrintStmt:
    expression: Expression


@dataclass
class InputStmt:
    name: str
    prompt: Optional[Expression]


@dataclass
class IfStmt:
    condition: Expression
    then_body: List["Statement"]
    else_body: Optional[List["Statement"]]


@dataclass
class WhileStmt:
    condition: Expression
    body: List["Statement"]


@dataclass
class FunctionDef:
    name: str
    parameters: List[str]
    body: List["Statement"]


@dataclass
class ReturnStmt:
    value: Optional[Expression]


@dataclass
class ExprStmt:
    expression: Expression


Statement = Union[
    VarDecl,
    Assign,
    PrintStmt,
    InputStmt,
    IfStmt,
    WhileStmt,
    FunctionDef,
    ReturnStmt,
    ExprStmt,
]


@dataclass
class Program:
    statements: List[Statement]
