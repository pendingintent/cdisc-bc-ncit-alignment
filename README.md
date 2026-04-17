# cdisc-bc-ncit-alignment

Tools for aligning [CDISC Biomedical Concepts (BCs)](https://www.cdisc.org/standards/semantics/biomedical-concepts) with [NCI Thesaurus (NCIt)](https://ncit.nci.nih.gov/ncitbrowser/) codes. Populates a master workbook (`Complete List.xlsx`) with the full NCIt concept catalogue and annotates each row with whether — and where — it is published in the CDISC Library.

## What it does

Starting from the column headers in `files/Complete List.xlsx`, the project runs two stages:

1. **`populate_complete_list`** — calls the NCIt EVS REST API once for the full code list, then fetches concept details in concurrent batches and writes every concept (~212,000 rows) to `output/Complete List.xlsx` with the 12 NCIt columns: code, preferred name, status, semantic type, NCI/CDISC definitions, synonyms, parents, children, and active flag.
2. **`augment_cdisc`** — calls the CDISC Library COSMOS endpoint `/mdr/bc/biomedicalconcepts` once, builds an NCIt→BC index from the returned HAL links, and appends three columns to each row: `Exists in CDISC`, `CDISC href`, `CDISC title`.

## Requirements

- **Python 3.14** (a `.venv/` lives at the project root — activate it with `source .venv/bin/activate`)
- **`CDISC_API_KEY`** environment variable (required for stage 2). Obtain one from the [CDISC Library](https://www.cdisc.org/cdisc-library).
- Dependencies: `openpyxl`, `requests`, `pytest` (install with `pip install openpyxl requests pytest`)

## Install

```bash
git clone <repo-url>
cd cdisc-bc-ncit-alignment
python3.14 -m venv .venv
source .venv/bin/activate
pip install openpyxl requests pytest
export CDISC_API_KEY=<your-key>
```

## Usage

### Stage 1 — populate from NCIt

```bash
python -m src.populate_complete_list                              # full ~212k codes
python -m src.populate_complete_list --limit 500                  # smoke test
python -m src.populate_complete_list --batch-size 500 --workers 12
python -m src.populate_complete_list --output output/mine.xlsx
```

Flags:
- `--output` — destination `.xlsx` (default `output/Complete List.xlsx`, must end with `.xlsx`)
- `--template` — template whose header row is copied (default `files/Complete List.xlsx`)
- `--batch-size` — NCIt list endpoint batch size (default 200; URL-length ceiling near 500)
- `--workers` — concurrent request workers (default 8)
- `--limit` — cap the number of codes for smoke tests

### Stage 2 — augment with CDISC BCs

```bash
python -m src.augment_cdisc                                       # in place on output/Complete List.xlsx
python -m src.augment_cdisc --input output/mine.xlsx              # in place on --input
python -m src.augment_cdisc --input in.xlsx --output out.xlsx     # separate files
```

Flags:
- `--input` — source `.xlsx` produced by stage 1 (default `output/Complete List.xlsx`)
- `--output` — destination; defaults to `--input` for an in-place update (inline updates use a temp file + atomic rename so a crash can't corrupt the source)

## Output schema

`output/Complete List.xlsx`, Sheet1, columns in order:

| # | Column | Source |
|---|---|---|
| 1 | NCI Concept Code | `/concept/ncit/codes` |
| 2 | Preferred Name (name) | `name` |
| 3 | Concept  Status | `conceptStatus` |
| 4 | Semantic Type | unique `properties.value` where `properties.type == "Semantic_Type"` |
| 5 | NCI Definition | `definitions.definition` where `source == "NCI"` |
| 6 | CDISC Definition | `definitions.definition` where `source == "CDISC"` |
| 7 | Synonyms | unique `synonyms.name`, sorted, `;`-joined |
| 8 | Parent  Concept Code | unique `parents.code`, sorted, `;`-joined |
| 9 | Parent Concept Name | `parents.name` in the same order |
| 10 | Child Concept Code | unique `children.code`, sorted, `;`-joined |
| 11 | Child Concept Name | `children.name` in the same order |
| 12 | Active (True/False) | `active` |
| 13 | Exists in CDISC | `True` iff the NCIt code is the trailing path segment of a `/mdr/bc/biomedicalconcepts/*` href |
| 14 | CDISC href | matching `_links.biomedicalConcepts[].href` |
| 15 | CDISC title | matching `_links.biomedicalConcepts[].title` |

The column-derivation rules in the project's [`CLAUDE.md`](./CLAUDE.md) are authoritative; `src/ncit_mapping.py` and `src/cdisc_mapping.py` implement them.

## Tests

```bash
python -m pytest tests -q
```

The suite is hermetic — no network calls. It covers column mapping (dedup, sort, missing fields), the CDISC HAL index build, and CLI path validation.

## Project layout

```
src/
  ncit_client.py           Retry/backoff HTTP + concurrent batching against EVS REST
  ncit_mapping.py          Pure NCIt-concept → Excel-row transforms
  populate_complete_list.py  Stage 1 CLI; streams rows via openpyxl write_only
  cdisc_client.py          Retry/backoff HTTP against CDISC COSMOS (API key via env)
  cdisc_mapping.py         Builds the NCIt→BC index from the HAL response
  augment_cdisc.py         Stage 2 CLI; streams input → output with 3 appended columns
  cli_utils.py             Shared argparse validators (e.g. .xlsx extension)
tests/                     Mapping and CLI-validator tests (no network)
files/                     Reference workbooks, governance docs (inputs, not generated)
output/                    Generated workbooks
.claude/agents/            Project-scoped Claude Code subagents for interactive lookups
CLAUDE.md                  Claude Code guidance + authoritative column-mapping rules
```

## External APIs

- **NCIt EVS REST** — `https://api-evsrest.nci.nih.gov/api/v1` (no key required). The list endpoint `/concept/ncit?list=...&include=...` enforces roughly a 150 s response floor and rejects URLs longer than ~500 comma-separated codes with HTTP 414.
- **CDISC Library COSMOS** — `https://api.library.cdisc.org/api/cosmos/v2` (header `api-key: $CDISC_API_KEY`). The `/mdr/bc/biomedicalconcepts` endpoint currently returns ~1,345 BCs.

## Performance

End-to-end refresh on a home connection: ~2.5 min for stage 1 (424 batches × 500 codes at 12 workers) and ~25 s for stage 2. Both stages stream rows through `openpyxl` write-only mode so memory stays flat at ~100 MB regardless of row count.

## License

See repository for license details.
