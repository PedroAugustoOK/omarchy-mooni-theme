#!/usr/bin/env python3
"""Regression checks for generated editor colors (no desktop changes)."""
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def contrast(a, b):
    def lum(value):
        c = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return sum(v * w for v, w in zip(c, (0.2126, 0.7152, 0.0722)))
    a, b = lum(a), lum(b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def main():
    subprocess.run([sys.executable, ROOT / "scripts/generate-code-theme.py", "--check"], check=True)
    palette = tomllib.loads((ROOT / "colors.toml").read_text())
    contract = tomllib.loads((ROOT / "code-colors.toml").read_text())
    vs = json.loads((ROOT / "vscode-theme.json").read_text())
    hx = tomllib.loads((ROOT / "helix.toml").read_text())
    zed = json.loads((ROOT / "integrations/zed.json").read_text())["themes"][0]
    require(vs["type"] == zed["appearance"] == palette["mode"], "editor appearance differs")
    require(not any(k.startswith("syntax.") for k in zed["style"]), "invalid Zed syntax structure")
    minimum = 100
    for kind, role in contract["syntax"].items():
        expected = palette[role]
        require(zed["style"]["syntax"][kind]["color"] == expected, f"Zed: {kind}")
        require(hx["palette"]["syntax_" + kind] == expected, f"Helix palette: {kind}")
        ratio = contrast(expected, palette["background"])
        minimum = min(minimum, ratio)
        require(ratio >= 4.5, f"{kind} contrast {ratio:.2f} is below 4.5")
        if kind in vs["semanticTokenColors"]:
            actual = vs["semanticTokenColors"][kind]
            if isinstance(actual, dict):
                actual = actual["foreground"]
            require(actual == expected, f"VS Code: {kind}")
    for scope, role in {
        "keyword": "keyword", "function": "function", "function.macro": "macro",
        "type": "type", "string": "string", "constant.numeric": "number",
        "constant": "constant", "variable.parameter": "property",
        "operator": "operator", "comment": "comment", "punctuation": "punctuation",
    }.items():
        require(hx["palette"][hx[scope]] == palette[contract["syntax"][role]], f"Helix scope: {scope}")
    for scope, value in hx.items():
        if scope == "palette":
            continue
        refs = [value] if isinstance(value, str) else [value[k] for k in ("fg", "bg") if k in value]
        for ref in refs:
            require(ref in hx["palette"], f"Undefined Helix color: {scope} -> {ref}")
    for state in ("activeSelection", "inactiveSelection", "focus", "hover"):
        fg, bg = (vs["colors"]["list." + state + suffix] for suffix in ("Foreground", "Background"))
        require(contrast(fg, bg) >= 4.5, f"Unreadable list state: {state}")
    for kind, role in contract["diagnostics"].items():
        require(hx["palette"]["diagnostic_" + kind] == palette[role], f"Helix diagnostic: {kind}")
    print(f"Editor semantics, UI states and syntax contrast verified (minimum {minimum:.2f}:1).")


if __name__ == "__main__":
    main()
