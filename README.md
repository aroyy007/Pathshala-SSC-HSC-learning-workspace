# Pathshala

Pathshala is a bilingual study assistant for the four selected SSC/HSC Bangla textbooks. A student chooses one paper, asks in Bengali, English, or Banglish, and receives a concise answer grounded in retrieved textbook evidence with page-linked citations.

The repository contains the React client, FastAPI backend, local ingestion tools, Kaggle GPU indexing pipeline, evaluation scripts, and the product/technical specifications needed to operate the project. The first release is deliberately limited to textbook question answering. Board questions, licensed solutions, notebook features, Bengali audio, and narrated lessons are later modules with separate provenance and review requirements.

## Current status

The application foundation is implemented. The four source PDFs and audit artifacts are kept in the ignored local `data/` directory, but the final reviewed indexes have not yet been imported into `data/indexes/`. Until that gate is complete, the app can be inspected and tested as a system but should not be presented as a verified textbook answer service.

The current pilot stack is:

- React, TypeScript, Vite, and Bengali-safe typography in `apps/web/`.
- FastAPI, Pydantic, SQLite, and local session ownership in `backend/`.
- Qwen3-Embedding-0.6B for dense embeddings, BM25 plus reciprocal-rank fusion for retrieval, and Gemini for structured answer generation.
- PaddleOCR-VL/Tesseract fallback and Qwen embedding generation in Kaggle for the four-book corpus.

## Repository map

```text
.
├── apps/web/                 React/Vite study interface
├── backend/eduapp/           FastAPI app and domain modules
├── backend/tests/            Backend regression tests
├── scripts/                  Audit, OCR, ingestion, import, and evaluation CLIs
├── kaggle/                   GPU OCR/indexing notebook runbook and builder
├── docs/                     Product, architecture, API, operations, and ADRs
├── research/                 Reviewed skill provenance and research records
├── CONTEXT.md                Canonical domain vocabulary
├── Makefile                  Common local commands
├── .env.example              Names of local environment variables only
└── pytest.ini                Test discovery configuration
```

The `data/` directory is intentionally ignored. It can contain source PDFs, OCR text, model caches, SQLite state, and private indexes.

## Quick start

Prerequisites:

- Python 3.12
- Node.js 20 or newer and pnpm
- A Gemini API key for live answer generation
- A Hugging Face token only if the selected embedding download requires it

Create the local environments and install dependencies:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r backend/requirements.lock
pnpm --dir apps/web install --frozen-lockfile
cp .env.example .env
```

Put credentials only in the ignored `.env` file. Never place them in frontend code, notebooks, source PDFs, fixtures, logs, or GitHub issues.

Run the backend and frontend in separate terminals:

```bash
make dev-api
make dev-web
```

Open <http://127.0.0.1:5173>. The Vite development server proxies `/api` and `/health` to the FastAPI process at port 8000.

Useful checks:

```bash
make test
make build
make audit
```

The API is served at <http://127.0.0.1:8000>. Its interactive OpenAPI document is available at `/docs` while the development server is running.

## Build the private indexes

The four PDFs must be named exactly:

```text
ssc-2026-bangla-1.pdf
ssc-2026-bangla-2.pdf
hsc-2026-bangla-1.pdf
hsc-2026-bangla-2.pdf
```

For the reliable long-running path, attach those four files as a private Kaggle dataset, enable a GPU, and follow [kaggle/RUN-ALL-KAGGLE.md](kaggle/RUN-ALL-KAGGLE.md). The notebook writes `/kaggle/working/pathshala-indexes.zip`.

Keep that ZIP private: it contains source PDFs, OCR output, and embeddings. After the OCR review gate, validate and import it locally:

```bash
.venv/bin/python scripts/import_kaggle_indexes.py \
  /absolute/path/pathshala-indexes.zip
```

The importer refuses invalid paths, mismatched hashes, malformed vectors, duplicate chunk IDs, incomplete manifests, and unreviewed output unless `--activate-unreviewed` is explicitly supplied for development.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — runtime components, data flow, boundaries, and failure handling.
- [API reference](docs/API.md) — implemented REST endpoints, request bodies, response shapes, errors, cookies, and rate limits.
- [Data and indexing](docs/DATA-AND-INDEXING.md) — source manifest, OCR checkpoints, chunking, index format, and import gates.
- [Evaluation](docs/EVALUATION.md) — retrieval, grounding, abstention, language, and release metrics.
- [Deployment](docs/DEPLOYMENT.md) — local, staging, and production deployment constraints.
- [Security](docs/SECURITY.md) — secrets, private corpus handling, request limits, and threat model.
- [Contributing](docs/CONTRIBUTING.md) — setup, verification, branch, and pull-request workflow.
- [Repository guide](docs/REPOSITORY.md) — ownership of each folder and generated-artifact policy.
- [Product requirements](docs/PRD.md), [technical requirements](docs/TRD.md), [UI/UX](docs/UIUX.md), [application flow](docs/APP-FLOW.md), and [backend schema](docs/BACKEND-SCHEMA.md).
- [Domain glossary](CONTEXT.md) and [accepted ADRs](docs/adr/).

## Release boundary

The assessment release is complete only when all four indexes pass the review gate, the API answers real Bengali/English/Banglish questions with valid citations, retrieval and abstention metrics are recorded, and the Python/Node setup is reproducible. The expanded learning platform is planned separately and must not contaminate the textbook authority boundary.

## License and source rights

This repository does not grant redistribution rights to the textbook PDFs, OCR text, embeddings, or generated media. Verify each source's rights before publishing any corpus artifact or deploying a public service. Add an explicit project license before accepting external contributions; do not infer one from the source textbooks.
