# -*- coding: utf-8 -*-
"""Run generated Python via the current interpreter or python on PATH."""

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class RunResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    log: str = ""


def find_python() -> Optional[str]:
    """Locate a Python executable (prefer the running interpreter)."""
    if sys.executable:
        return sys.executable
    return shutil.which("python3") or shutil.which("python")


def run_python(
    py_path: Path,
    timeout_seconds: int = 30,
    cwd: Optional[Path] = None,
) -> RunResult:
    """
    Execute a .py file with Python.
    Uses subprocess with UTF-8 encoding and timeout.
    """
    python = find_python()
    if not python:
        return RunResult(
            success=False,
            stderr="Python አልተገኘም።",
            log="Python not found",
            exit_code=-1,
        )
    if not py_path.exists():
        return RunResult(
            success=False,
            stderr=f"ፋይሉ አልተገኘም: {py_path}",
            exit_code=-1,
        )

    work_dir = str(cwd or py_path.parent)
    cmd: List[str] = [python, str(py_path.resolve())]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            cwd=work_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return RunResult(
            success=proc.returncode == 0,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            exit_code=proc.returncode,
            log=f"python {py_path.name} → exit {proc.returncode}",
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            success=False,
            stderr="ፕሮግራሙ በጊዜ ማለቂያ ቆመ",
            log="Process timed out",
            exit_code=-1,
        )
    except Exception as e:
        return RunResult(
            success=False,
            stderr=f"ስህተት: {e}",
            log=str(e),
            exit_code=-1,
        )
