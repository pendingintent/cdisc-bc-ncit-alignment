"""Thin HTTP client for the CDISC Library COSMOS Biomedical Concepts API."""

from __future__ import annotations

import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.library.cdisc.org/api/cosmos/v2"


def make_session() -> requests.Session:
    """Return a requests Session preloaded with retry, API key, and JSON Accept header."""
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    api_key = os.environ.get("CDISC_API_KEY")
    if not api_key:
        raise RuntimeError("CDISC_API_KEY environment variable is not set")
    s.headers.update({"api-key": api_key, "Accept": "application/json"})
    return s


def fetch_biomedical_concepts(session: requests.Session | None = None, timeout: int = 120) -> dict:
    """Fetch the COSMOS biomedical concepts index as a JSON dict."""
    s = session or make_session()
    r = s.get(f"{BASE_URL}/mdr/bc/biomedicalconcepts", timeout=timeout)
    r.raise_for_status()
    return r.json()
