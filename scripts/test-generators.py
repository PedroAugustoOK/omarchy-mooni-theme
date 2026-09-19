#!/usr/bin/env python3
"""Exercise generators in an isolated clone-like directory."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(root, *args):
    return subprocess.run([sys.executable, root / "scripts/generate-code-theme.py", *args],
                          capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory(prefix="omarchy-editor-tests-") as temp:
        root = Path(temp) / "arbitrary-clone-name"
        (root / "scripts").mkdir(parents=True)
        for name in ("colors.toml", "code-colors.toml", "theme.toml", "scripts/generate-code-theme.py"):
            shutil.copy2(ROOT / name, root / name)
        result = run(root)
        if result.returncode:
            raise RuntimeError(result.stderr)
        expected_name = json.loads((ROOT / "vscode-theme.json").read_text())["name"]
        if json.loads((root / "vscode-theme.json").read_text())["name"] != expected_name:
            raise RuntimeError("Theme name depends on checkout directory")
        outputs = [root / "vscode-theme.json", root / "helix.toml",
                   *sorted((root / "integrations").iterdir())]
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in outputs}
        if run(root, "--check").returncode:
            raise RuntimeError("Fresh generation was rejected")
        if before != {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in outputs}:
            raise RuntimeError("--check changed files")
        for path in outputs:
            original = path.read_bytes()
            path.write_text("stale fixture\n")
            if run(root, "--check").returncode == 0:
                raise RuntimeError(f"Stale output not detected: {path}")
            if path.read_text() != "stale fixture\n":
                raise RuntimeError("--check repaired a file instead of only checking")
            path.write_bytes(original)
        missing = root / "integrations/zed.json"
        missing.unlink()
        if run(root, "--check").returncode == 0 or missing.exists():
            raise RuntimeError("Missing output not detected or --check created it")
    print("Regression tests passed: clone name, stale/missing files, read-only check.")


if __name__ == "__main__":
    main()
