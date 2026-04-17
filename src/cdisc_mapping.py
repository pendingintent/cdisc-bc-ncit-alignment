"""Extract NCIt -> CDISC biomedical-concept linkage from the CDISC Library COSMOS API.

The `/mdr/bc/biomedicalconcepts` endpoint returns a HAL-style document whose
`_links.biomedicalConcepts` array holds one entry per published BC. The last
path segment of each entry's `href` is the NCIt C-code, e.g.::

    /mdr/bc/biomedicalconcepts/C105585  ->  C105585
"""

from __future__ import annotations

from typing import Any


def ncit_code_from_href(href: str) -> str:
    """Return the trailing path segment (the NCIt code) of a CDISC BC href."""
    return href.rsplit("/", 1)[-1]


def build_index(response: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Return {ncit_code: {"href": ..., "title": ...}} for every BC in the response.

    The CDISC API can emit multiple BCs sharing the same NCIt code; first occurrence wins
    so downstream lookups are deterministic.
    """
    links = (response.get("_links") or {}).get("biomedicalConcepts") or []
    index: dict[str, dict[str, str]] = {}
    for item in links:
        href = item.get("href")
        if not href:
            continue
        code = ncit_code_from_href(href)
        if code and code not in index:
            index[code] = {"href": href, "title": item.get("title") or ""}
    return index


def lookup(index: dict[str, dict[str, str]], ncit_code: str) -> tuple[bool, str, str]:
    """Return (exists, href, title) for the given NCIt code."""
    hit = index.get(ncit_code)
    if hit is None:
        return False, "", ""
    return True, hit["href"], hit["title"]
