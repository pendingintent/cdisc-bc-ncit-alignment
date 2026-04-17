"""Tests for src.cdisc_mapping."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cdisc_mapping import build_index, lookup, ncit_code_from_href  # noqa: E402


def _response() -> dict:
    return {
        "_links": {
            "biomedicalConcepts": [
                {
                    "href": "/mdr/bc/biomedicalconcepts/C105585",
                    "title": "Glucose Measurement",
                    "type": "Biomedical Concept",
                },
                {
                    "href": "/mdr/bc/biomedicalconcepts/C147905",
                    "title": "Urine Dipstick Test",
                    "type": "Biomedical Concept",
                },
                # duplicate NCIt code — first occurrence should win
                {
                    "href": "/mdr/bc/biomedicalconcepts/C105585",
                    "title": "Second Glucose Entry",
                },
                # missing title should not explode
                {"href": "/mdr/bc/biomedicalconcepts/C999"},
                # missing href should be skipped
                {"title": "no href"},
            ]
        }
    }


def test_ncit_code_from_href():
    assert ncit_code_from_href("/mdr/bc/biomedicalconcepts/C12345") == "C12345"
    assert ncit_code_from_href("C999") == "C999"


def test_build_index_maps_code_to_href_and_title():
    idx = build_index(_response())
    assert idx["C105585"] == {
        "href": "/mdr/bc/biomedicalconcepts/C105585",
        "title": "Glucose Measurement",
    }
    assert idx["C147905"]["title"] == "Urine Dipstick Test"


def test_build_index_first_occurrence_wins_on_duplicates():
    idx = build_index(_response())
    assert idx["C105585"]["title"] == "Glucose Measurement"


def test_build_index_handles_missing_fields():
    idx = build_index(_response())
    assert idx["C999"]["title"] == ""
    assert all(code != "" for code in idx)


def test_lookup_hit_returns_true_with_href_and_title():
    idx = build_index(_response())
    assert lookup(idx, "C147905") == (True, "/mdr/bc/biomedicalconcepts/C147905", "Urine Dipstick Test")


def test_lookup_miss_returns_false_with_empty_strings():
    idx = build_index(_response())
    assert lookup(idx, "C_missing") == (False, "", "")


def test_build_index_empty_when_no_links():
    assert build_index({}) == {}
    assert build_index({"_links": {}}) == {}
    assert build_index({"_links": {"biomedicalConcepts": []}}) == {}
