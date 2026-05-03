"""Small CLI to print banner files from the `services.api.utils.branding` package.

Usage:
  python3 -m services.api.utils.print_banner completion

It prefers importlib.resources (works when packaged) and falls back
to reading `services/api/utils/branding/*.txt` by path. It also replaces a
`{{PROJECT_NAME}}` placeholder from the `PROJECT_NAME` environment
variable if present.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from importlib import resources
except ImportError:  # pragma: no cover - importlib is available on py3
    resources = None  # type: ignore[assignment]


def _read_with_importlib(package: str, filename: str) -> str:
    try:
        return resources.read_text(package, filename, encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return ""


def _read_with_path(filename: str) -> str:
    p = Path(__file__).resolve().parent / "branding" / filename
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return ""


def read_banner(name: str) -> str:
    """Return banner text for the given banner `name`.

    The function first attempts to read the resource using
    `importlib.resources` (works when the package is installed). If that
    fails, it falls back to reading the file from the repository path
    `app/utils/branding/<name>.txt`.

    Args:
        name: Banner name or filename (with or without `.txt`).

    Returns:
        The banner content as a string, or an empty string if not found.
    """
    filename = name if name.endswith(".txt") else f"{name}.txt"

    # 1) Try importlib.resources (works in installed packages)
    if resources is not None:
        content = _read_with_importlib("services.api.utils.branding", filename)
        if content:
            return content

    # 2) Fallback: read from repository path
    content = _read_with_path(filename)
    return content


def replace_placeholders(content: str) -> str:
    """Replace supported placeholders in banner content.

    Currently supported placeholders:
    - `{{PROJECT_NAME}}`: replaced with the value of the `PROJECT_NAME`
      environment variable if it is set.

    Args:
        content: The banner content containing zero or more placeholders.

    Returns:
        The banner content with placeholders substituted (or the original
        content if no applicable environment variables are set).
    """
    project_name = os.environ.get("PROJECT_NAME")
    if project_name:
        return content.replace("{{PROJECT_NAME}}", project_name)
    return content


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint to print a banner file.

    Args:
        argv: Optional list of command-line arguments. If omitted, the
            function will use `sys.argv[1:]`. The first argument is the
            banner name (without `.txt`) to print; defaults to
            `'completion'`.

    Returns:
        Exit code (0 on success, 2 if the banner was not found).
    """
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
