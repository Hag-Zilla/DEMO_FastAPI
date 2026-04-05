"""Branding and ASCII art loader for the Expense Tracker API.

This module reads plain-text banner files from `app/utils/branding/` so
that banners live outside scripts and can be `cat`-ed by shell
or imported by Python.
"""

from __future__ import annotations

import os

BASE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "utils", "branding")
)


def _read_banner(filename: str) -> str:
    path = os.path.join(BASE_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return ""


# Expose commonly used banners as constants (loaded from files)
STARTUP_BANNER = _read_banner("startup.txt")
LOG_SIGNATURE = "🎯 Expense Tracker API - Powered by Hagzilla"


def get_banner(name: str) -> str:
    """Return banner content by filename (e.g. 'completion.txt')."""
    return _read_banner(name)
