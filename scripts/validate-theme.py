#!/usr/bin/env python3
"""Validate the files required by this Omarchy theme."""

import re
import struct
import subprocess
import sys
import tomllib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODE = "light"
REQUIRED = {
    "ATTRIBUTIONS.md",
    "INTEGRATIONS.md",
    "LICENSE",
    "README.md",
    "btop.theme",
    "colors.toml",
    "icons.theme",
    "preview-unlock.png",
    "preview.png",
    "shell.toml",
    "unlock.png",
}
INTEGRATIONS = {
    "bat.conf",
    "cava-theme",
    "delta.gitconfig",
    "fastfetch.jsonc",
    "fzf.fish",
    "lazygit.yml",
    "steam.css",
    "superfile.toml",
    "vencord.theme.css",
    "yazi-theme.toml",
    "zed.json",
}
SHELL_SECTIONS = {
    "bar", "controls", "spacing", "font", "popups", "tooltip",
    "notifications", "launcher", "menu", "polkit", "lock", "image-picker",
}


def luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    one, two = luminance(first), luminance(second)
    return (max(one, two) + 0.05) / (min(one, two) + 0.05)


def png_size(path):
    with path.open("rb") as image:
        assert image.read(8) == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
        image.read(4)
        assert image.read(4) == b"IHDR", f"{path.name} has no IHDR"
        return struct.unpack(">II", image.read(8))


def main():
    missing = sorted(name for name in REQUIRED if not (ROOT / name).is_file())
    assert not missing, f"missing files: {', '.join(missing)}"

    palette = tomllib.loads((ROOT / "colors.toml").read_text())
    assert palette.get("mode") == MODE, f"mode must be {MODE!r}"
    colors = {key: value for key, value in palette.items() if key != "mode"}
    assert len(colors) >= 20
    assert all(re.fullmatch(r"#[0-9A-Fa-f]{6}", value) for value in colors.values())
    assert contrast(palette["foreground"], palette["background"]) >= 7
    assert contrast(palette["accent"], palette["background"]) >= 4.5
    assert contrast(palette["muted"], palette["background"]) >= 4.5

    shell = tomllib.loads((ROOT / "shell.toml").read_text())
    assert SHELL_SECTIONS <= set(shell), "shell.toml is incomplete"
    palette_values = {value.lower() for value in colors.values()}
    for filename in ("shell.toml", "btop.theme"):
        used = {value.lower() for value in re.findall(r"#[0-9A-Fa-f]{6}", (ROOT / filename).read_text())}
        assert used <= palette_values, f"{filename} has a color outside colors.toml"

    btop = (ROOT / "btop.theme").read_text()
    assert f'theme[main_bg]="{palette["background"]}"' in btop
    assert f'theme[main_fg]="{palette["foreground"]}"' in btop
    assert (ROOT / "icons.theme").read_text().strip() == "Yaru-yellow"

    integration_dir = ROOT / "integrations"
    integration_files = {path.name for path in integration_dir.iterdir() if path.is_file()}
    assert INTEGRATIONS <= integration_files, "integration support is incomplete"
    for path in integration_dir.iterdir():
        if not path.is_file():
            continue
        used = {value.lower() for value in re.findall(r"#[0-9A-Fa-f]{6}", path.read_text())}
        assert used <= palette_values, f"{path.name} has a color outside colors.toml"

    json.loads((integration_dir / "fastfetch.jsonc").read_text())
    json.loads((integration_dir / "zed.json").read_text())
    tomllib.loads((integration_dir / "superfile.toml").read_text())
    tomllib.loads((integration_dir / "yazi-theme.toml").read_text())
    generated = subprocess.run(
        [sys.executable, ROOT / "scripts" / "generate-integrations.py", "--check"],
        text=True,
        capture_output=True,
    )
    assert generated.returncode == 0, generated.stderr.strip()

    for filename in ("preview.png", "preview-unlock.png"):
        width, height = png_size(ROOT / filename)
        assert width >= 1000 and height >= 500
        assert abs(width / height - 16 / 9) < 0.03

    wallpapers = sorted((ROOT / "backgrounds").glob("*.png"))
    assert len(wallpapers) == 4, "exactly four wallpapers are required"
    assert all(png_size(path) == (3840, 2160) for path in wallpapers)

    print(
        f"Validated {len(colors)} colors, {len(wallpapers)} wallpapers, "
        f"and {len(INTEGRATIONS)} optional integrations."
    )


if __name__ == "__main__":
    main()
