"""Tests for src.cli_utils."""

from __future__ import annotations

import argparse
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cli_utils import validate_xlsx_path, xlsx_path  # noqa: E402


def test_accepts_xlsx_extension():
    p = pathlib.Path("output/Complete List.xlsx")
    assert validate_xlsx_path(p) is p


def test_accepts_uppercase_extension():
    p = pathlib.Path("FILE.XLSX")
    assert validate_xlsx_path(p) is p


def test_rejects_missing_extension():
    with pytest.raises(argparse.ArgumentTypeError, match=r"must end with \.xlsx"):
        validate_xlsx_path(pathlib.Path("report"))


def test_rejects_wrong_extension():
    with pytest.raises(argparse.ArgumentTypeError, match=r"\.csv"):
        validate_xlsx_path(pathlib.Path("report.csv"))


def test_xlsx_path_factory_returns_path():
    coerce = xlsx_path("--output")
    assert coerce("out/file.xlsx") == pathlib.Path("out/file.xlsx")


def test_xlsx_path_factory_raises_with_label():
    coerce = xlsx_path("--output")
    with pytest.raises(argparse.ArgumentTypeError, match=r"--output"):
        coerce("report.txt")
