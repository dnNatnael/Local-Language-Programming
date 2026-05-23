# -*- coding: utf-8 -*-
"""
Integrates with the existing AML translator (in-memory API).
Does not reimplement lexer/parser/codegen.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

# Project root: PL/ (parent of amharic_editor/)
PL_ROOT = Path(__file__).resolve().parents[2]
if str(PL_ROOT) not in sys.path:
    sys.path.insert(0, str(PL_ROOT))


@dataclass
class TranslateResult:
    success: bool
    python: str = ""
    output_path: Optional[Path] = None
    error_message: str = ""
    error_line: int = 0
    error_column: int = 0
    log: str = ""


def _parse_amharic_error(msg: str) -> Tuple[str, int, int]:
    """Extract line/column from formatted AmharicSyntaxError string."""
    line, col = 0, 0
    if "ረድፍ" in msg:
        try:
            part = msg.split("ረድፍ")[1]
            line = int(part.split(",")[0].strip().split()[0].strip("("))
            if "አምድ" in part:
                col = int(part.split("አምድ")[1].strip().split()[0])
        except (ValueError, IndexError):
            pass
    return msg, line, col


def translate_source(
    source: str,
    aml_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> TranslateResult:
    """
    Translate AML source to Python using existing translator.translate().
    """
    try:
        from translator import translate
        from src.errors import AmharicSyntaxError
    except ImportError as e:
        return TranslateResult(
            success=False,
            error_message=f"ተርጓሚ አልተገኘም: {e}",
            log=str(e),
        )

    try:
        py = translate(source)
        out = output_path
        if out is None and aml_path:
            out = aml_path.with_suffix(".py")
        if out:
            out.write_text(py, encoding="utf-8")
            log = f"ተተርጉሟል → {out}"
        else:
            log = "ተተርጉሟል (በማህደር)"
        return TranslateResult(
            success=True,
            python=py,
            output_path=out,
            log=log,
        )
    except Exception as e:
        from src.errors import AmharicSyntaxError
        if isinstance(e, AmharicSyntaxError):
            msg, line, col = _parse_amharic_error(str(e))
            return TranslateResult(
                success=False,
                error_message=msg,
                error_line=line,
                error_column=col,
                log=msg,
            )
        return TranslateResult(
            success=False,
            error_message=f"ስህተት: {e}",
            log=str(e),
        )


def translate_file(aml_path: Path, output_path: Optional[Path] = None) -> TranslateResult:
    """Translate an .aml file on disk."""
    if not aml_path.exists():
        return TranslateResult(
            success=False,
            error_message=f"ፋይሉ አልተገኘም: {aml_path}",
        )
    source = aml_path.read_text(encoding="utf-8")
    return translate_source(source, aml_path=aml_path, output_path=output_path)
