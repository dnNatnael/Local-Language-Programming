# -*- coding: utf-8 -*-
"""Non-GUI smoke tests for editor integration."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(EDITOR))

from integration.translator_runner import translate_file
from integration.python_runner import run_python, find_python


def main():
    aml = ROOT / "examples" / "01_variables.aml"
    if not aml.exists():
        aml = ROOT / "መግቢያ፡ኢት" / "01_variables.፡ኢት"
    tr = translate_file(aml)
    assert tr.success, tr.error_message
    assert "print(" in tr.python
    print("translate: OK")

    if find_python():
        run = run_python(tr.output_path)
        assert "105" in run.stdout, run.stdout
        print("run:", run.stdout.strip())
    else:
        print("run: skipped (python not installed)")

    print("All smoke tests passed.")


if __name__ == "__main__":
    main()
