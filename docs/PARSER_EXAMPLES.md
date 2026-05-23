# Parser — AST and Parsing Examples

## AST Node Classes

| Node | Fields | Meaning |
|------|--------|---------|
| `Program` | `statements` | Root |
| `VarDecl` | `var_type`, `name`, `initializer` | `ቁጥር` / `ጽሑፍ` declaration |
| `Assign` | `name`, `value` | Reassignment |
| `PrintStmt` | `expression` | `አትም` |
| `IfStmt` | `condition`, `then_body`, `else_body` | `ከሆነ` / `ካልሆነ` |
| `WhileStmt` | `condition`, `body` | `እስከ` |
| `FunctionDef` | `name`, `parameters`, `body` | `ተግባር` |
| `ReturnStmt` | `value` | `መልስ` |
| `BinaryOp` | `left`, `operator`, `right` | e.g. `+`, `==` |
| `CallExpr` | `callee`, `arguments` | `ድምር(5, 3)` |

## Example — While Loop AST (conceptual)

Source:

```aml
እስከ i < 5
    አትም i
    i = i + 1
መጨረሻ
```

AST shape:

```
WhileStmt
├── condition: BinaryOp(<, Identifier(i), NumberLiteral(5))
└── body:
    ├── PrintStmt(Identifier(i))
    └── Assign(i, BinaryOp(+, Identifier(i), NumberLiteral(1)))
```

## Example — Function AST

Source:

```aml
ተግባር ድምር(a, b)
    መልስ a + b
መጨረሻ
```

```
FunctionDef(name='ድምር', parameters=['a','b'],
  body=[ReturnStmt(BinaryOp(+, Identifier(a), Identifier(b)))])
```

## Block Parsing

`_parse_block_until(KW_ELSE, KW_END)` reads statements until `ካልሆነ` or `መጨረሻ` without consuming the stop token. The caller then handles `else` or requires `መጨረሻ`.

## Error Example

Missing `መጨረሻ`:

```
ስህተት (ረድፍ 3, አምድ 1): መጨረሻ ተጠበቀ
```
