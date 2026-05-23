# -*- coding: utf-8 -*-
"""Load user guide documents from YAML files."""

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

USER_GUIDE_DIR = Path(__file__).resolve().parents[1] / "docs" / "user_guide"

# Default colors (dark theme) — readable in QTextBrowser
DEFAULT_COLORS = {
    "background": "#1e1e1e",
    "foreground": "#e0e0e0",
    "heading": "#4fc3f7",
    "subheading": "#ce93d8",
    "code_bg": "#2d2d2d",
    "code_fg": "#d4d4d4",
    "border": "#404040",
}


@dataclass
class GuideSection:
    heading: str
    body: str = ""
    code_example: str = ""


@dataclass
class UserGuideDocument:
    path: Path
    title: str
    order: int
    sections: List[GuideSection] = field(default_factory=list)


def _parse_sections(raw_sections: Any) -> List[GuideSection]:
    if not raw_sections:
        return []
    sections: List[GuideSection] = []
    for item in raw_sections:
        if not isinstance(item, dict):
            continue
        sections.append(
            GuideSection(
                heading=str(item.get("heading", "")),
                body=str(item.get("body", "")).strip(),
                code_example=str(item.get("code_example", "")).strip(),
            )
        )
    return sections


def load_user_guides(guide_dir: Optional[Path] = None) -> List[UserGuideDocument]:
    """Load all *.yml user guides from the guide directory, sorted by order."""
    directory = guide_dir or USER_GUIDE_DIR
    if not directory.is_dir():
        return []

    try:
        import yaml
    except ImportError:
        return []

    documents: List[UserGuideDocument] = []
    for path in sorted(directory.glob("*.yml")):
        try:
            data: Dict[str, Any] = yaml.safe_load(
                path.read_text(encoding="utf-8")
            )
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        documents.append(
            UserGuideDocument(
                path=path,
                title=str(data.get("title", path.stem)),
                order=int(data.get("order", 999)),
                sections=_parse_sections(data.get("sections")),
            )
        )
    documents.sort(key=lambda d: (d.order, d.path.name))
    return documents


def _font_family_css() -> str:
    try:
        from editor.fonts import ETHIOPIC_UI_FAMILIES
        families = ", ".join(f"'{f}'" for f in ETHIOPIC_UI_FAMILIES[:6])
    except ImportError:
        families = "'Segoe UI', 'Noto Sans Ethiopic', sans-serif"
    return families


def _wrap_html(body: str, colors: Dict[str, str]) -> str:
    """Full HTML document so QTextBrowser renders all text with correct colors."""
    ff = _font_family_css()
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
  background-color: {colors['background']};
  color: {colors['foreground']};
  font-family: {ff};
  font-size: 11pt;
  line-height: 1.55;
  margin: 0;
  padding: 16px;
}}
h2 {{
  color: {colors['heading']};
  font-size: 14pt;
  margin: 0 0 12px 0;
  border-bottom: 1px solid {colors['border']};
  padding-bottom: 6px;
}}
h3 {{
  color: {colors['subheading']};
  font-size: 12pt;
  margin: 18px 0 8px 0;
}}
p {{
  margin: 0 0 10px 0;
}}
pre {{
  background-color: {colors['code_bg']};
  color: {colors['code_fg']};
  font-family: {ff}, Consolas, 'Cascadia Mono', monospace;
  font-size: 10pt;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid {colors['border']};
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  margin: 0 0 14px 0;
}}
hr {{
  border: none;
  border-top: 1px solid {colors['border']};
  margin: 24px 0;
}}
.toc {{
  background: {colors['code_bg']};
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
}}
.toc li {{ margin: 4px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def _render_sections_html(
    doc: UserGuideDocument,
    colors: Dict[str, str],
    include_title: bool = True,
) -> str:
    parts: List[str] = []
    if include_title:
        parts.append(f"<h2>{escape(doc.title)}</h2>")
    for sec in doc.sections:
        if sec.heading:
            parts.append(f"<h3>{escape(sec.heading)}</h3>")
        if sec.body:
            body_html = "<br>".join(escape(line) for line in sec.body.split("\n"))
            parts.append(f"<p>{body_html}</p>")
        if sec.code_example:
            parts.append(f"<pre>{escape(sec.code_example)}</pre>")
    return "".join(parts)


def render_document_html(
    doc: UserGuideDocument,
    colors: Optional[Dict[str, str]] = None,
) -> str:
    """Render one guide document as HTML for QTextBrowser."""
    c = {**DEFAULT_COLORS, **(colors or {})}
    return _wrap_html(_render_sections_html(doc, c), c)


def render_all_documents_html(
    documents: List[UserGuideDocument],
    colors: Optional[Dict[str, str]] = None,
) -> str:
    """Render every guide in one scrollable document."""
    c = {**DEFAULT_COLORS, **(colors or {})}
    parts = [
        "<div class='toc'><strong>መረጃ ገጾች</strong><ol>",
    ]
    for doc in documents:
        parts.append(f"<li>{escape(doc.title)}</li>")
    parts.append("</ol></div>")

    for i, doc in enumerate(documents):
        if i > 0:
            parts.append("<hr>")
        parts.append(_render_sections_html(doc, c, include_title=True))

    return _wrap_html("".join(parts), c)


def theme_to_colors(theme_name: str) -> Dict[str, str]:
    """Map editor theme name to guide HTML colors."""
    try:
        from editor.themes import get_theme
        t = get_theme(theme_name)
        if theme_name == "light":
            return {
                "background": t.background,
                "foreground": t.foreground,
                "heading": "#1565c0",
                "subheading": "#6a1b9a",
                "code_bg": "#f5f5f5",
                "code_fg": "#333333",
                "border": t.border,
            }
        return {
            "background": t.background,
            "foreground": t.foreground,
            "heading": "#4fc3f7",
            "subheading": "#ce93d8",
            "code_bg": "#2d2d2d",
            "code_fg": t.foreground,
            "border": t.border,
        }
    except ImportError:
        return dict(DEFAULT_COLORS)
