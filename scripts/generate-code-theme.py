#!/usr/bin/env python3
"""Generate editor syntax themes from the shared semantic color contract."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE = tomllib.loads((ROOT / "colors.toml").read_text())
CONTRACT = tomllib.loads((ROOT / "code-colors.toml").read_text())
OUT = ROOT / "integrations"
THEME_NAME = {"OmarchyTheme": "Ankh", "OmarchyAnkhDark": "Ankh Dark"}.get(ROOT.name, ROOT.name.removeprefix("Omarchy"))

def color(name: str) -> str:
    return PALETTE[name]

syntax = {key: color(value) for key, value in CONTRACT["syntax"].items()}
diagnostics = {key: color(value) for key, value in CONTRACT["diagnostics"].items()}

zed = {
    "$schema": "https://zed.dev/schema/themes/v0.1.0.json",
    "name": f"Omarchy {THEME_NAME}",
    "author": "Pedro Augusto",
    "themes": [{
        "name": f"Omarchy {THEME_NAME}",
        "appearance": "light" if PALETTE["mode"] == "light" else "dark",
        "style": {
            "background": color("background"),
            "editor.background": color("background"),
            "editor.foreground": color("foreground"),
            "text": color("foreground"),
            "text.muted": color("muted"),
            "border": color("darker_background"),
            "panel.background": color("dark_background"),
            "title_bar.background": color("background"),
            "status_bar.background": color("dark_background"),
            "tab.active_background": color("selection"),
            "element.hover": color("selection"),
            "element.selected": color("selection"),
            "editor.active_line.background": color("dark_background"),
            "editor.gutter.background": color("background"),
            "terminal.background": color("background"),
            "terminal.foreground": color("foreground"),
            "syntax.comment": syntax["comment"],
            "syntax.keyword": syntax["keyword"],
            "syntax.function": syntax["function"],
            "syntax.string": syntax["string"],
            "syntax.number": syntax["number"],
            "syntax.type": syntax["type"],
            "syntax.operator": syntax["operator"],
        },
    }],
}

helix = f'''# Generated from code-colors.toml; do not edit directly.
"keyword" = "accent"
"keyword.control" = {{ fg = "accent", modifiers = ["italic"] }}
"function" = "blue"
"function.builtin" = "blue"
"function.macro" = "cyan"
"type" = "yellow"
"type.builtin" = "yellow"
"constructor" = "blue"
"constant" = "bright_yellow"
"constant.builtin" = "bright_yellow"
"constant.numeric" = "orange"
"string" = "green"
"string.regexp" = "green"
"string.special" = "cyan"
"comment" = {{ fg = "muted", modifiers = ["italic"] }}
"variable" = "foreground"
"variable.parameter" = {{ fg = "foreground", modifiers = ["italic"] }}
"variable.other.member" = "cyan"
"operator" = "cyan"
"tag" = "blue"
"namespace" = "yellow"
"attribute" = "yellow"
"punctuation" = "muted"

"markup.heading" = "accent"
"markup.link.url" = {{ fg = "blue", modifiers = ["underlined"] }}
"markup.link.text" = "accent"
"markup.raw" = "green"
"markup.quote" = "muted"

"diff.plus" = "green"
"diff.minus" = "red"
"diff.delta" = "orange"

"ui.background" = {{ }}
"ui.text" = "foreground"
"ui.text.inactive" = "muted"
"ui.linenr" = {{ fg = "muted" }}
"ui.selection" = {{ bg = "selection_background", fg = "selection_foreground" }}
"ui.cursor" = {{ fg = "background", bg = "cursor" }}
"ui.statusline" = {{ fg = "background", bg = "foreground" }}
"ui.statusline.normal" = {{ fg = "background", bg = "blue", modifiers = ["bold"] }}
"ui.statusline.insert" = {{ fg = "background", bg = "green", modifiers = ["bold"] }}
"ui.statusline.select" = {{ fg = "background", bg = "accent", modifiers = ["bold"] }}
"diagnostic.error" = {{ underline = {{ color = "red", style = "curl" }} }}
"diagnostic.warning" = {{ underline = {{ color = "yellow", style = "curl" }} }}
"diagnostic.info" = {{ underline = {{ color = "blue", style = "curl" }} }}
"diagnostic.hint" = {{ underline = {{ color = "cyan", style = "curl" }} }}
error = "red"
warning = "yellow"
info = "blue"
hint = "cyan"

[palette]
background = "{color("background")}"
foreground = "{color("foreground")}"
lighter_background = "{color("lighter_background")}"
cursor = "{color("bright_foreground")}"
selection_background = "{color("selection")}"
selection_foreground = "{color("foreground")}"
accent = "{color("accent")}"
muted = "{color("muted")}"
red = "{color("red")}"
yellow = "{color("yellow")}"
orange = "{color("orange")}"
green = "{color("green")}"
cyan = "{color("cyan")}"
blue = "{color("blue")}"
bright_yellow = "{color("bright_yellow")}"
'''

vscode = {
    "$schema": "vscode://schemas/color-theme",
    "name": f"Omarchy {THEME_NAME}",
    "type": "light" if PALETTE["mode"] == "light" else "dark",
    "semanticHighlighting": True,
    "semanticTokenColors": {
        "parameter": syntax["property"], "property": syntax["property"],
        "variable": color("foreground"), "function": syntax["function"],
        "method": syntax["function"], "class": syntax["type"],
        "interface": syntax["type"], "enum": syntax["type"],
        "type": syntax["type"], "typeParameter": syntax["type"],
        "string": syntax["string"], "number": syntax["number"],
        "boolean": syntax["number"], "operator": syntax["operator"],
        "keyword": syntax["keyword"], "macro": syntax["macro"],
        "decorator": syntax["decorator"],
        "comment": {"foreground": syntax["comment"], "fontStyle": "italic"},
    },
    "colors": {
        "editor.foreground": color("foreground"),
        "editor.background": color("background"),
        "editor.selectionBackground": color("selection") + "80",
        "editorError.foreground": diagnostics["error"],
        "editorWarning.foreground": diagnostics["warning"],
        "editorInfo.foreground": diagnostics["info"],
        "focusBorder": color("accent"),
    },
}

OUT.mkdir(exist_ok=True)
(OUT / "helix.toml").write_text(helix)
(OUT / "vscode-theme.json").write_text(json.dumps(vscode, indent=2) + "\n")
print("Generated integrations/helix.toml and vscode-theme.json")
