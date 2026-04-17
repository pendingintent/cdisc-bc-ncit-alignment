"""Pure transforms from an NCIt EVS concept payload to Complete List.xlsx row values.

Column order (1-indexed) matches files/Complete List.xlsx Sheet1:
  1  NCI Concept Code
  2  Preferred Name (name)
  3  Concept  Status
  4  Semantic Type
  5  NCI Definition
  6  CDISC Definition
  7  Synonyms
  8  Parent  Concept Code
  9  Parent Concept Name
 10  Child Concept Code
 11  Child Concept Name
 12  Active (True/False)
"""

from __future__ import annotations

from typing import Any, Iterable

SEP = ";"


def _semantic_types(concept: dict[str, Any]) -> str:
    """Join unique `Semantic_Type` property values with the column separator."""
    values: list[str] = []
    seen: set[str] = set()
    for prop in concept.get("properties") or ():
        if prop.get("type") == "Semantic_Type":
            v = prop.get("value")
            if v and v not in seen:
                seen.add(v)
                values.append(v)
    return SEP.join(values)


def _definition_for(concept: dict[str, Any], source: str) -> str | None:
    """Return the first definition string matching the given source, or None."""
    for d in concept.get("definitions") or ():
        if d.get("source") == source:
            return d.get("definition")
    return None


def _synonyms(concept: dict[str, Any]) -> str:
    """Return synonym names deduped and sorted, joined by the column separator."""
    seen: set[str] = set()
    ordered: list[str] = []
    for s in concept.get("synonyms") or ():
        name = s.get("name")
        if name and name not in seen:
            seen.add(name)
            ordered.append(name)
    return SEP.join(sorted(ordered))


def _related(concept: dict[str, Any], key: str) -> tuple[str, str]:
    """Return (codes_joined, names_joined) sorted by code, deduped."""
    seen: dict[str, str] = {}
    for r in concept.get(key) or ():
        c = r.get("code")
        n = r.get("name")
        if c and c not in seen:
            seen[c] = n or ""
    codes_sorted = sorted(seen)
    names_sorted = [seen[c] for c in codes_sorted]
    return SEP.join(codes_sorted), SEP.join(names_sorted)


def concept_to_row(concept: dict[str, Any]) -> list[Any]:
    """Map one NCIt concept payload (include=full,children,definitions,...) to a row."""
    parent_codes, parent_names = _related(concept, "parents")
    child_codes, child_names = _related(concept, "children")
    return [
        concept.get("code"),
        concept.get("name"),
        concept.get("conceptStatus"),
        _semantic_types(concept),
        _definition_for(concept, "NCI"),
        _definition_for(concept, "CDISC"),
        _synonyms(concept),
        parent_codes,
        parent_names,
        child_codes,
        child_names,
        concept.get("active"),
    ]


def concepts_to_rows(concepts: Iterable[dict[str, Any]]) -> list[list[Any]]:
    """Map a batch of NCIt concept payloads to a list of row value lists."""
    return [concept_to_row(c) for c in concepts]
