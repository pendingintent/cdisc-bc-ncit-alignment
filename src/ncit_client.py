"""Thin HTTP client for the NCIt EVS REST API.

Batches concept detail fetches via the list endpoint so we issue ~212k/BATCH_SIZE
requests instead of one per code, and runs batches concurrently.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api-evsrest.nci.nih.gov/api/v1"
# include list kept explicit so children/definitions are guaranteed to come back
INCLUDE = "synonyms,definitions,properties,parents,children"


def make_session(pool: int = 32) -> requests.Session:
    """Return a requests Session with retry/backoff and a sized connection pool."""
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=pool, pool_maxsize=pool)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"Accept": "application/json"})
    return s


def fetch_all_codes(session: requests.Session | None = None, timeout: int = 120) -> list[str]:
    """Fetch the full list of NCIt concept codes from the EVS REST API."""
    s = session or make_session()
    r = s.get(f"{BASE_URL}/concept/ncit/codes", timeout=timeout)
    r.raise_for_status()
    return r.json()


def _chunks(seq: list[str], size: int) -> Iterator[list[str]]:
    """Yield successive `size`-length slices of `seq`."""
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def fetch_batch(session: requests.Session, codes: list[str], timeout: int = 120) -> list[dict]:
    """Fetch full concept details for one batch of NCIt codes."""
    params = {"list": ",".join(codes), "include": INCLUDE}
    r = session.get(f"{BASE_URL}/concept/ncit", params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_concepts(
    codes: Iterable[str],
    session: requests.Session | None = None,
    batch_size: int = 200,
    max_workers: int = 8,
    on_progress: Callable[[int, int], None] | None = None,
) -> Iterator[dict]:
    """Yield concept dicts. Batches are submitted concurrently; yield order is not
    guaranteed to match input order — callers must key by concept['code']."""
    s = session or make_session(pool=max_workers * 2)
    code_list = list(codes)
    total_batches = (len(code_list) + batch_size - 1) // batch_size
    done_batches = 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(fetch_batch, s, chunk) for chunk in _chunks(code_list, batch_size)]
        for fut in as_completed(futures):
            batch = fut.result()
            done_batches += 1
            if on_progress:
                on_progress(done_batches, total_batches)
            for concept in batch:
                yield concept


def throttle(min_interval_s: float) -> Callable[[], None]:
    """Return a callable that sleeps so successive calls are spaced by at least
    min_interval_s seconds. Use when tuning request rate for a shared API."""
    state = {"last": 0.0}

    def tick() -> None:
        now = time.monotonic()
        wait = min_interval_s - (now - state["last"])
        if wait > 0:
            time.sleep(wait)
        state["last"] = time.monotonic()

    return tick
