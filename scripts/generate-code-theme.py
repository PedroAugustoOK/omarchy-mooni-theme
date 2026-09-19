#!/usr/bin/env python3
"""Generate editor syntax themes from the shared semantic color contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE = tomllib.loads((ROOT / "colors.toml").read_text())
CONTRACT = tomllib.loads((ROOT / "code-colors.toml").read_text())
OUT = ROOT / "integrations"
THEME_NAME = tomllib.loads((ROOT / "theme.toml").read_text())["name"]

def color(name: str) -> str:
    return PALETTE[name]

syntax = {key: color(value) for key, value in CONTRACT["syntax"].items()}
diagnostics = {key: color(value) for key, value in CONTRACT["diagnostics"].items()}

zed = {
    "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
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
            "syntax": {
                key: {"color": value, **({"font_style": "italic"} if key == "comment" else {})}
                for key, value in syntax.items()
            },
        },
    }],
}

helix = f'''# Generated from code-colors.toml; do not edit directly.
"keyword" = "syntax_keyword"
"keyword.control" = "syntax_keyword"
"function" = "syntax_function"
"function.builtin" = "syntax_function"
"function.macro" = "syntax_macro"
"type" = "syntax_type"
"type.builtin" = "syntax_type"
"constructor" = "syntax_function"
"constant" = "syntax_constant"
"constant.builtin" = "syntax_constant"
"constant.numeric" = "syntax_number"
"string" = "syntax_string"
"string.regexp" = "syntax_string"
"string.special" = "syntax_operator"
"comment" = "syntax_comment"
"variable" = "foreground"
"variable.parameter" = "syntax_property"
"variable.other.member" = "syntax_property"
"operator" = "syntax_operator"
"tag" = "syntax_decorator"
"namespace" = "syntax_type"
"attribute" = "syntax_decorator"
"punctuation" = "syntax_punctuation"

"markup.heading" = "accent"
"markup.link.url" = {{ fg = "blue", modifiers = ["underlined"] }}
"markup.link.text" = "accent"
"markup.raw" = "green"
"markup.quote" = "muted"

"diff.plus" = "green"
"diff.minus" = "red"
"diff.delta" = "orange"

"ui.background" = {{ fg = "foreground", bg = "background" }}
"ui.text" = "foreground"
"ui.text.inactive" = "muted"
"ui.linenr" = {{ fg = "muted" }}
"ui.selection" = {{ bg = "selection_background", fg = "selection_foreground" }}
"ui.cursor" = {{ fg = "background", bg = "cursor" }}
"ui.statusline" = {{ fg = "background", bg = "foreground" }}
"ui.statusline.normal" = {{ fg = "background", bg = "blue", modifiers = ["bold"] }}
"ui.statusline.insert" = {{ fg = "background", bg = "green", modifiers = ["bold"] }}
"ui.statusline.select" = {{ fg = "background", bg = "accent", modifiers = ["bold"] }}
"diagnostic.error" = {{ underline = {{ color = "diagnostic_error", style = "curl" }} }}
"diagnostic.warning" = {{ underline = {{ color = "diagnostic_warning", style = "curl" }} }}
"diagnostic.info" = {{ underline = {{ color = "diagnostic_info", style = "curl" }} }}
"diagnostic.hint" = {{ underline = {{ color = "diagnostic_hint", style = "curl" }} }}
error = "diagnostic_error"
warning = "diagnostic_warning"
info = "diagnostic_info"
hint = "diagnostic_hint"

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

helix += "".join(f'syntax_{key} = "{value}"\n' for key, value in syntax.items())
helix += "".join(f'diagnostic_{key} = "{value}"\n' for key, value in diagnostics.items())

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
        "boolean": syntax["constant"], "enumMember": syntax["constant"],
        "variable.readonly": syntax["constant"], "operator": syntax["operator"],
        "keyword": syntax["keyword"], "macro": syntax["macro"],
        "decorator": syntax["decorator"],
        "comment": {"foreground": syntax["comment"], "fontStyle": "italic"},
    },
    "tokenColors": [
        {"scope": ["comment", "punctuation.definition.comment"], "settings": {"foreground": syntax["comment"], "fontStyle": "italic"}},
        {"scope": ["string", "constant.other.symbol"], "settings": {"foreground": syntax["string"]}},
        {"scope": ["constant.numeric", "constant.character"], "settings": {"foreground": syntax["number"]}},
        {"scope": ["constant.language", "variable.other.constant"], "settings": {"foreground": syntax["constant"]}},
        {"scope": ["keyword", "storage", "storage.type", "storage.modifier"], "settings": {"foreground": syntax["keyword"]}},
        {"scope": ["entity.name.function", "support.function"], "settings": {"foreground": syntax["function"]}},
        {"scope": ["entity.name.type", "entity.name.class", "support.type", "support.class"], "settings": {"foreground": syntax["type"]}},
        {"scope": ["keyword.operator", "punctuation.accessor", "punctuation.separator"], "settings": {"foreground": syntax["operator"]}},
        {"scope": ["variable", "variable.other", "meta.definition.variable"], "settings": {"foreground": color("foreground")}},
        {"scope": ["variable.parameter", "variable.other.property", "support.variable.property"], "settings": {"foreground": syntax["property"]}},
        {"scope": ["entity.name.tag", "entity.other.attribute-name"], "settings": {"foreground": syntax["decorator"]}},
        {"scope": ["punctuation", "meta.brace"], "settings": {"foreground": syntax["punctuation"]}},
    ],
    "colors": {
        "editor.foreground": color("foreground"),
        "editor.background": color("background"),
        "editorLineNumber.foreground": color("muted"),
        "editorLineNumber.activeForeground": color("accent"),
        "editorCursor.foreground": color("accent"),
        "editor.lineHighlightBackground": color("dark_background") + "80",
        "editor.selectionBackground": color("selection"),
        "activityBar.background": color("dark_background"),
        "activityBar.foreground": color("foreground"),
        "activityBar.activeBorder": color("accent"),
        "sideBar.background": color("dark_background"),
        "sideBar.foreground": color("foreground"),
        "sideBar.border": color("darker_background"),
        "tab.activeBackground": color("background"),
        "tab.inactiveBackground": color("dark_background"),
        "statusBar.background": color("accent"),
        "statusBar.foreground": color("background"),
        "titleBar.activeBackground": color("background"),
        "titleBar.activeForeground": color("foreground"),
        "editorError.foreground": diagnostics["error"],
        "editorWarning.foreground": diagnostics["warning"],
        "editorInfo.foreground": diagnostics["info"],
        "focusBorder": color("accent"),
    },
}

# Complete commonly visible UI states instead of inheriting unrelated default colors.
ui_roles = {
    "foreground": "foreground", "descriptionForeground": "muted",
    "disabledForeground": "muted", "errorForeground": "code_error",
    "editor.selectionForeground": "foreground",
    "editor.inactiveSelectionBackground": "selection",
    "list.activeSelectionBackground": "selection", "list.activeSelectionForeground": "foreground",
    "list.inactiveSelectionBackground": "selection", "list.inactiveSelectionForeground": "foreground",
    "list.focusBackground": "selection", "list.focusForeground": "foreground",
    "list.hoverBackground": "dark_background", "list.hoverForeground": "foreground",
    "list.highlightForeground": "accent", "activityBar.inactiveForeground": "muted",
    "editorGroupHeader.tabsBackground": "dark_background",
    "tab.activeForeground": "foreground", "tab.inactiveForeground": "muted",
    "tab.activeBorderTop": "accent", "tab.border": "dark_background",
    "titleBar.inactiveBackground": "dark_background", "titleBar.inactiveForeground": "muted",
    "panel.background": "background", "panel.border": "darker_background",
    "panelTitle.activeForeground": "foreground", "panelTitle.inactiveForeground": "muted",
    "panelTitle.activeBorder": "accent",
    "input.background": "background", "input.foreground": "foreground",
    "input.border": "muted", "input.placeholderForeground": "muted",
    "dropdown.background": "dark_background", "dropdown.foreground": "foreground",
    "dropdown.border": "muted", "button.background": "accent", "button.foreground": "background",
    "badge.background": "accent", "badge.foreground": "background",
    "statusBar.noFolderBackground": "accent", "statusBar.noFolderForeground": "background",
    "statusBar.debuggingBackground": "accent", "statusBar.debuggingForeground": "background",
    "editorWidget.background": "dark_background", "editorWidget.foreground": "foreground",
    "editorWidget.border": "muted",
    "editorSuggestWidget.background": "dark_background", "editorSuggestWidget.foreground": "foreground",
    "editorSuggestWidget.selectedBackground": "selection",
    "editorSuggestWidget.selectedForeground": "foreground",
    "editorSuggestWidget.highlightForeground": "accent",
    "menu.background": "dark_background", "menu.foreground": "foreground",
    "menu.selectionBackground": "selection", "menu.selectionForeground": "foreground",
    "notifications.background": "dark_background", "notifications.foreground": "foreground",
    "terminal.background": "background", "terminal.foreground": "foreground",
}
vscode["colors"].update({key: color(role) for key, role in ui_roles.items()})
for index, role in enumerate(("code_function", "code_type", "code_property", "code_keyword", "code_string", "code_number"), 1):
    vscode["colors"][f"editorBracketHighlight.foreground{index}"] = color(role)
ansi = {
    "Black": "background", "Red": "red", "Green": "green", "Yellow": "yellow",
    "Blue": "blue", "Magenta": "magenta", "Cyan": "cyan", "White": "light_foreground",
    "BrightBlack": "muted", "BrightRed": "bright_red", "BrightGreen": "bright_green",
    "BrightYellow": "bright_yellow", "BrightBlue": "bright_blue", "BrightMagenta": "bright_magenta",
    "BrightCyan": "bright_cyan", "BrightWhite": "bright_foreground",
}
for name, role in ansi.items():
    vscode["colors"][f"terminal.ansi{name}"] = color(role)
    zed_name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    zed["themes"][0]["style"][f"terminal.ansi.{zed_name}"] = color(role)

zed["themes"][0]["style"].update(diagnostics)
vscode["colors"]["editorHint.foreground"] = diagnostics["hint"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check generated files without writing")
    args = parser.parse_args()
    outputs = {
        ROOT / "vscode-theme.json": json.dumps(vscode, indent=2) + "\n",
        ROOT / "helix.toml": helix,
        OUT / "vscode-theme.json": json.dumps(vscode, indent=2) + "\n",
        OUT / "helix.toml": helix,
        OUT / "zed.json": json.dumps(zed, indent=2) + "\n",
    }
    stale = []
    for path, content in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("Stale generated files: " + ", ".join(stale), file=sys.stderr)
        raise SystemExit(1)
    print(f"{'Checked' if args.check else 'Generated'} {len(outputs)} editor theme files.")


if __name__ == "__main__":
    main()
