"""Tests for src.ncit_mapping."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ncit_mapping import concept_to_row  # noqa: E402


def _concept() -> dict:
    return {
        "code": "C1000",
        "name": "Recombinant Amphiregulin",
        "conceptStatus": "DEFAULT",
        "active": True,
        "synonyms": [
            {"name": "AR"},
            {"name": "AMPHIREGULIN"},
            {"name": "AR"},  # dup
            {"name": "Recombinant Amphiregulin"},
        ],
        "definitions": [
            {"source": "NCI", "definition": "NCI def."},
            {"source": "CDISC", "definition": "CDISC def."},
            {"source": "Other", "definition": "ignored"},
        ],
        "properties": [
            {"type": "Semantic_Type", "value": "Amino Acid, Peptide, or Protein"},
            {"type": "Semantic_Type", "value": "Pharmacologic Substance"},
            {"type": "Other", "value": "ignored"},
        ],
        "parents": [
            {"code": "C1504", "name": "Recombinant EGF"},
            {"code": "C1000", "name": "Dup"},  # unused in real data; just exercise dedup
            {"code": "C1504", "name": "Recombinant EGF"},  # dup
        ],
        "children": [
            {"code": "C2", "name": "B child"},
            {"code": "C1", "name": "A child"},
        ],
    }


def test_basic_scalar_columns():
    row = concept_to_row(_concept())
    assert row[0] == "C1000"
    assert row[1] == "Recombinant Amphiregulin"
    assert row[2] == "DEFAULT"
    assert row[11] is True


def test_semantic_types_joined_with_semicolon():
    row = concept_to_row(_concept())
    assert row[3] == "Amino Acid, Peptide, or Protein;Pharmacologic Substance"


def test_definitions_pick_source():
    row = concept_to_row(_concept())
    assert row[4] == "NCI def."
    assert row[5] == "CDISC def."


def test_missing_definitions_are_none():
    c = _concept()
    c["definitions"] = [{"source": "NCI", "definition": "only NCI"}]
    row = concept_to_row(c)
    assert row[4] == "only NCI"
    assert row[5] is None


def test_synonyms_deduped_and_sorted():
    row = concept_to_row(_concept())
    # sorted set joined by semicolon
    assert row[6] == "AMPHIREGULIN;AR;Recombinant Amphiregulin"


def test_parents_sorted_by_code_deduped():
    row = concept_to_row(_concept())
    assert row[7] == "C1000;C1504"
    assert row[8] == "Dup;Recombinant EGF"


def test_children_sorted_by_code():
    row = concept_to_row(_concept())
    assert row[9] == "C1;C2"
    assert row[10] == "A child;B child"


def test_missing_lists_become_empty_strings():
    c = {"code": "C9", "name": "x", "conceptStatus": "DEFAULT", "active": False}
    row = concept_to_row(c)
    assert row == ["C9", "x", "DEFAULT", "", None, None, "", "", "", "", "", False]
