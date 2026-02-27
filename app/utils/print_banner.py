"""Small CLI to print banner files from the `app.branding` package.

Usage:
  python3 -m app.utils.print_banner completion

It prefers importlib.resources (works when packaged) and falls back
to reading `app/branding/*.txt` by path. It also replaces a
`{{PROJECT_NAME}}` placeholder from the `PROJECT_NAME` environment
variable if present.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from importlib import resources
except Exception:  # pragma: no cover - importlib is available on py3
    resources = None


def _read_with_importlib(package: str, filename: str) -> str:
    try:
        return resources.read_text(package, filename, encoding="utf-8")
    except Exception:
        return ""


def _read_with_path(project_root: Path, filename: str) -> str:
    p = project_root / "app" / "branding" / filename
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def read_banner(name: str) -> str:
    filename = name if name.endswith(".txt") else f"{name}.txt"

    # 1) Try importlib.resources (works in installed packages)
    if resources is not None:
        content = _read_with_importlib("app.branding", filename)
        if content:
            return content

    # 2) Fallback: read from repository path
    project_root = Path(__file__).resolve().parents[1]
    content = _read_with_path(project_root, filename)
    return content


def replace_placeholders(content: str) -> str:
    project_name = os.environ.get("PROJECT_NAME")
    if project_name:
        return content.replace("{{PROJECT_NAME}}", project_name)
    return content


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    name = argv[0] if argv else "completion"

    content = read_banner(name)
    if not content:
        print(f"Banner '{name}' not found", file=sys.stderr)
        return 2

    content = replace_placeholders(content)
    print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
