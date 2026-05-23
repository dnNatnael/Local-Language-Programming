# -*- coding: utf-8 -*-
"""AML keyword definitions — shared by highlighter, autocomplete, and UI."""

from typing import List, Tuple

# (Amharic keyword, English name, short description in Amharic)
AML_KEYWORD_ENTRIES: List[Tuple[str, str, str]] = [
    ("አትም", "print", "ውጤት ማተም"),
    ("ግቤት", "input", "ከተጠቃሚ ግቤት"),
    ("ከሆነ", "if", "አገሣጸር"),
    ("ካልሆነ", "else", "ካልሆነ ቅርጽ"),
    ("እስከ", "while", "ድገም"),
    ("ተግባር", "function", "ተግባር መግለጽ"),
    ("መልስ", "return", "መልስ ሰጥ"),
    ("መጨረሻ", "end", "ብሎክ መጨረሻ"),
    ("እውነት", "true", "እውነት"),
    ("ሐሰት", "false", "ሐሰት"),
    ("ቁጥር", "number", "ቁጥር ተሟላ"),
    ("ጽሑፍ", "text", "ጽሑፍ ተሟላ"),
    ("እና", "and", "እና (logic)"),
    ("ወይም", "or", "ወይም (logic)"),
    ("አይደለም", "not", "አይደለም (logic)"),
]

# Flat list for syntax highlighter / completer
AML_KEYWORDS: List[str] = [entry[0] for entry in AML_KEYWORD_ENTRIES]
