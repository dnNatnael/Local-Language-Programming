# -*- coding: utf-8 -*-
"""Dark and light theme color definitions for the AML editor."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EditorTheme:
    name: str
    background: str
    foreground: str
    line_number_bg: str
    line_number_fg: str
    current_line: str
    selection: str
    keyword: str
    string: str
    number: str
    comment: str
    function: str
    operator: str
    identifier: str
    border: str
    sidebar_bg: str
    panel_bg: str
    toolbar_bg: str
    status_bg: str
    accent: str
    error: str


THEMES: Dict[str, EditorTheme] = {
    "dark": EditorTheme(
        name="dark",
        background="#181820",
        foreground="#e0e4ec",
        line_number_bg="#1e1e28",
        line_number_fg="#5c6370",
        current_line="#1a2030",
        selection="#23478a",
        keyword="#7ab8ff",
        string="#d2a67a",
        number="#b8d19a",
        comment="#6a9955",
        function="#e2c77a",
        operator="#c9cdd8",
        identifier="#78c8ff",
        border="#363844",
        sidebar_bg="#1e1e28",
        panel_bg="#181820",
        toolbar_bg="#28283a",
        status_bg="#1a6fa0",
        accent="#4a9eff",
        error="#f07171",
    ),
    "light": EditorTheme(
        name="light",
        background="#ffffff",
        foreground="#1e1e1e",
        line_number_bg="#f7f6f3",
        line_number_fg="#6e7681",
        current_line="#fff9c4",
        selection="#b4d4fe",
        keyword="#0055cc",
        string="#b5200d",
        number="#0a5f0a",
        comment="#008000",
        function="#795e26",
        operator="#1e1e1e",
        identifier="#0b67d2",
        border="#d9dde4",
        sidebar_bg="#f7f6f3",
        panel_bg="#ffffff",
        toolbar_bg="#ededed",
        status_bg="#1a6fa0",
        accent="#0066cc",
        error="#c41e3a",
    ),
}


def get_theme(name: str) -> EditorTheme:
    return THEMES.get(name, THEMES["dark"])


def editor_stylesheet(theme: EditorTheme) -> str:
    return f"""QPlainTextEdit {{
        background-color: {theme.background};
        color: {theme.foreground};
        border: none;
        font-family: 'Cascadia Mono', 'Consolas', 'Noto Sans Ethiopic', 'Abyssinica SIL', monospace;
        font-size: 11pt;
        selection-background-color: {theme.selection};
        selection-color: #ffffff;
        caret-color: {theme.accent};
        placeholder-color: rgba(150, 160, 170, 160);
    }}
"""
