# Repository guide

## Ownership map

| Path | Owns | Generated/private content |
| --- | --- | --- |
| `apps/web/` | Student-facing React client | `dist/`, `node_modules/` ignored |
| `backend/eduapp/` | API and application domain modules | Runtime SQLite is under `data/` |
| `backend/tests/` | Fast, deterministic backend tests | No private book text in fixtures |
| `scripts/` | Local corpus and evaluation commands | Outputs belong under ignored `data/` or `artifacts/` |
| `kaggle/` | Reproducible GPU indexing notebook assets | Kaggle outputs contain private source material |
| `docs/` | Product, engineering, operations, and decisions | Do not embed secrets or protected source text |
| `research/` | Research and skill provenance | Keep only review metadata and licenses |
| `data/` | Local PDFs, OCR, indexes, models, SQLite | Always ignored by Git |

## Naming conventions

- Python modules and functions use `snake_case`.
- Collection IDs are lowercase, stable, and hyphenated.
- REST resources are plural lowercase nouns under `/api/v1`.
- Corpus versions are immutable 20-character IDs derived from source and pipeline hashes.
- Documentation filenames use uppercase legacy names for the original specifications and uppercase descriptive names for new engineering guides.

## What belongs in Git

Commit source code, tests, lockfiles, configuration examples, schemas, runbooks, ADRs, and redacted evaluation format examples. Do not commit `.env`, PDFs, OCR JSON, vectors, model caches, SQLite state, `dist/`, or provider responses containing source text.

## What should be split later

When the system grows, separate ingestion workers, storage adapters, evaluation datasets, and media-generation jobs into their own packages. Keep the public API and domain identifiers stable during that split.
