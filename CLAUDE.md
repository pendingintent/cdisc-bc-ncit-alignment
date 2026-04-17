# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project supports the alignment of CDISC Biomedical Concepts (BCs) with NCI Thesaurus (NCIt) codes. CDISC BCs are standardized representations of clinical observations and measurements (e.g., vital signs, lab tests, ECG results) that map to SDTM/CDASH dataset variables. NCIt provides the controlled terminology (C-codes) that these concepts reference. API calls are used to populate the `files/Complete List.xlsx`.

## Code

- Follow Test driven development principles
- Focus on performance
- NCIt API base URL: https://api-evsrest.nci.nih.gov/api/v1
- CDISC Biomedical Concepts API base URL: https://api.library.cdisc.org/api/cosmos/v2
- Output files are stored in `output/`

## Domain Context

- **Biomedical Concepts (BCs)**: Informative (not normative) CDISC content developed using templates aligned with the BC and Dataset Specialization Logical Data Models.
- **NCIt codes**: Identifiers like `C12345` from the NCI Thesaurus used to standardize clinical terminology across CDISC standards.
- **CDISC Library**: The API and repository where BCs are published (provisional during review, final after approval). API base: `https://library.cdisc.org/api`.
- **BC Governance**: Content is governed by the Data Standards BC Curation Team, following a lifecycle: Scoping -> Development -> Draft -> Internal Review -> Public Review (30 days) -> Publication -> Maintenance (quarterly/semi-annual updates).

## Environment

- **Python**: 3.14 via `.venv` (activate with `source .venv/bin/activate`)
- **Reference documents**: `files/` directory contains Excel workbooks, governance docs, and curation guidelines — these are input/reference materials, not generated outputs
- **CDISC_API_KEY**: environmental parameter
- **Code directory**: `src/` stores executable code

## Key Reference Files

- `files/Complete List.xlsx` — master list of biomedical concepts (primary working data)
- `files/BC Examples.xlsx` — example BC definitions
- `files/BC DEC Templates.xlsx` — Data Element Concept templates for BC curation
- `files/BC Curation Principles and Completion GLs.xlsx` — curation rules and completion guidelines
- `files/BC Governance.pdf` — governance process documentation


###  `files/Complete List.xlsx` population

- Column `NCI Concept Code` populated using `https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/codes` .
- Use `https://api-evsrest.nci.nih.gov/api/v1/concept/ncit/{code}?include=full` to populate the values listed below:
    - Column `Preferred Name (name)` populated using `name` from the API repsonse.
    - Column `Concept  Status` populated using `conceptStatus` from the API repsonse.
    - Column `Semantic Type` populated using `properties.value` where `properties.type="Semantic_Type"`.
    - Column `NCI Definition` populated using `definitions.definition` where `definitions.source` = "NCI".
    - Column `CDISC Definition` populated using `definitions.definition` where `definitions.source` = "CDISC".
    - Column `Synonyms` populated using all values in `synonyms.name` added as a set to prevent duplicates and using semi-colons to separate multiple name values.
    - Column `Parent  Concept Code` populated using `parents.code`. If multiple values exist, added as a set to prevent duplicates, sort values by code and using semi-colons to separate multiple values.
    - Column `Parent Concept Name` populated using `parents.name`. If multiple values exist, added as a set to prevent duplicates, sort values by code and using semi-colons to separate multiple values.
    - Column `Child Concept Code` populated using `children.code`. If multiple values exist, added as a set to prevent duplicates, sort values by code and using semi-colons to separate multiple values.
    - Column `Child Concept Name` populated using `children.name`. If multiple values exist, added as a set to prevent duplicates, sort values by code and using semi-colons to separate multiple values.
    - Column `Active (True/False)` poulated using `active`.