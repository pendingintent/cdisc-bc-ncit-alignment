"""Small helpers shared by the CLI entry points."""

from __future__ import annotations

import argparse
import pathlib


def validate_xlsx_path(path: pathlib.Path, *, label: str = "path") -> pathlib.Path:
    """Return `path` unchanged if it ends with `.xlsx` (case-insensitive).

    Raises argparse.ArgumentTypeError so the validator plugs directly into
    argparse as a `type=` argument; the message names which CLI flag failed
    via `label`.
    """
    if path.suffix.lower() != ".xlsx":
        raise argparse.ArgumentTypeError(
            f"{label} must end with .xlsx (got {path.name!r})"
        )
    return path


def xlsx_path(label: str):
    """Return an argparse `type=` callable that validates and returns a Path."""

    def _coerce(value: str) -> pathlib.Path:
        return validate_xlsx_path(pathlib.Path(value), label=label)

    return _coerce
