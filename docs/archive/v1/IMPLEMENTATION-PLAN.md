# Pathshala Implementation Plan

**Version:** 1.0

**Date:** 11 September 2026

**Goal:** Deliver a verified bilingual four-book RAG application with source citations and a polished student interface.

**Architecture:** A React web client talks to a modular FastAPI backend. An offline ingestion pipeline builds immutable, book-scoped dense and BM25 indexes. Gemini generates structured answers from retrieved evidence; the server validates citations before persistence.
**Source specifications:** [TRD](TRD.md), [Application flow](APP-FLOW.md), [UI/UX](UIUX.md), [Backend schema](BACKEND-SCHEMA.md), [PRD](PRD.md)

## 1. Current baseline

The repository already contains:

- the four PDFs under the ignored local data directory and source metadata files;
- a FastAPI application with corpus, session, message, evidence, PDF, saved-answer, feedback, status, and health endpoints;
- SQLite persistence with owner checks and 24-hour session cleanup;
- native PDF extraction, quality gating, deterministic chunking, Qwen embedding integration, NumPy exact search, BM25, and RRF;
- Gemini structured generation and exact quote/evidence-ID validation;
- a React/Vite study interface covering welcome, library, conversation, saved answers, evidence, preferences, and error states;
- PRD and RAG-method research documents.

This is in-progress source code. Dependency installation was interrupted by network timeouts, indexes have not been built, the browser UI has not been rendered and inspected, and no end-to-end accuracy claim is valid yet.

## 2. Global constraints

- Exactly four selected PDFs, one per paper, remain in release scope.
- Each session and every retrieval operation are pinned to one book and version.
- No secret enters tracked source, browser code, fixtures, logs, or documentation.
- PDF bytes and generated indexes remain outside Git unless distribution rights are explicitly cleared.
- Qwen3-Embedding-0.6B is the starting model; BGE-M3 is the required comparison.
- Gemini 3.5 Flash-Lite is the starting generator; stronger generation is an evaluated escalation.
- Reranking, OCR, PostgreSQL, and approximate vector search are added only at defined evidence gates.
- Completion claims require fresh commands and inspected outputs.

## 3. Milestone sequence

```mermaid
flowchart LR
  M0[0. Recover build] --> M1[1. Audit corpus]
  M1 --> M2[2. Validate ingestion]
  M2 --> M3[3. Verify retrieval]
  M3 --> M4[4. Verify generation API]
  M4 --> M5[5. Finish web UI]
  M5 --> M6[6. Add evaluation]
  M6 --> M7[7. Harden and release]
```

## 4. Milestone 0: Recover and freeze the build environment

**Outcome:** Both application projects install and produce reproducible lockfiles.

**Files:**

- Modify `.gitignore`, `.env.example`, `README.md`
- Create `backend/pyproject.toml` or pinned `backend/requirements.lock`
- Keep `apps/web/pnpm-lock.yaml`
- Add root task commands through a `Makefile` or documented scripts

**Tasks:**

- [ ] Inspect the partial Python and pnpm installations left by the network interruption.
- [ ] Retry only missing packages using the bundled Python and Node runtimes.
- [ ] Confirm `.env` is ignored, mode-restricted, and absent from Git history.
- [ ] Pin compatible dependency versions; avoid unconstrained production dependencies.
- [ ] Add `dev-api`, `dev-web`, `test`, `build`, `ingest`, and `evaluate` commands.
- [ ] Record the required Python, Node, and model-download disk requirements.

**Verification:**

```text
python -m pip check
python -c "import fastapi, fitz, sentence_transformers, httpx"
pnpm --dir apps/web install --frozen-lockfile
pnpm --dir apps/web build
git check-ignore .env data/raw/ssc-2026-bangla-1.pdf
```

## 5. Milestone 1: Audit the four source PDFs

**Outcome:** Every source has reviewed identity, coverage, text quality, and redistribution status.

**Files:**

- Modify `docs/PDF-SOURCES.md`
- Create `data/manifests/{book_id}.json` as ignored runtime artifacts
- Create `artifacts/corpus-audit/` as ignored review output
- Add `backend/tests/fixtures/pdfs/` with tiny synthetic or redistributable fixtures

**Tasks:**

- [ ] Verify file signature, SHA-256, byte count, page count, cover, publication page, and contents for each PDF.
- [ ] Compare book contents with the 2026 exam syllabus and record missing coverage.
- [ ] Confirm whether HSC Second Paper’s BOU source is acceptable for the intended curriculum.
- [ ] Render and inspect at least 20 representative pages per source, including poetry, prose, grammar rules, tables, and exercises.
- [ ] Create manual transcriptions for a text-quality sample and measure native extraction error.
- [ ] Decide per page whether native extraction, OCR, or exclusion is required.
- [ ] Keep all rights and syllabus uncertainty visible in the Book details contract.

**Verification:** Each manifest has no placeholder provenance field, each hash matches the local PDF, and every excluded page has a recorded reason.

## 6. Milestone 2: Make ingestion deterministic and trustworthy

**Outcome:** The same source and configuration produce identical chunks and a validated immutable index.

**Files:**

- Modify `backend/eduapp/ingest.py`, `retrieval.py`, `config.py`
- Create focused modules for `extract.py`, `normalize.py`, `chunk.py`, `manifest.py`
- Create `backend/tests/ingestion/`
- Create versioned pipeline configuration under `configs/`

**Tasks:**

- [ ] Split extraction, normalization, chunking, embedding, and activation into focused modules.
- [ ] Replace heuristic-only page quality with documented metrics and manual override support.
- [ ] Add OCR fallback for reviewed pages and preserve extraction method.
- [ ] Preserve raw, canonical, and search text separately.
- [ ] Implement page offsets and source-span validation.
- [ ] Use exact embedding revision, tokenizer revision, and prompt in the manifest.
- [ ] Build BM25 from persisted tokenization rather than reconstructing undocumented state.
- [ ] Write temporary artifacts in a unique build directory and activate only after validation.
- [ ] Keep a previous active index available while the new one builds.

**Tests:** Bengali marks survive normalization; chunks respect boundaries and token limits; empty or encrypted PDFs fail safely; duplicate ingestion is idempotent; mismatched dimensions and non-finite vectors prevent activation.

## 7. Milestone 3: Establish retrieval quality

**Outcome:** Hybrid retrieval has measured Bengali and English-to-Bengali performance per book.

**Files:**

- Modify `backend/eduapp/retrieval.py`
- Create `backend/eduapp/rerank.py` only if the gate is reached
- Create `evals/pilot.schema.json`, controlled evaluation data, and `backend/eduapp/evaluation/`
- Create `scripts/evaluate.py`

**Tasks:**

- [ ] Create 20 reviewed semantic groups per book with paired Bengali and English questions: 160 pilot queries total.
- [ ] Keep paired queries in the same development or validation split.
- [ ] Add answerable, unsupported, ambiguous, follow-up, factual, explanation, rule, and rule-application cases.
- [ ] Compute Hit@k, passage Recall@k, MRR, latency, memory, and per-example failures.
- [ ] Compare dense-only, BM25-only, and Qwen hybrid retrieval.
- [ ] Build a completely separate BGE-M3 index and repeat the comparison.
- [ ] Compare source-derived context prefix on and off.
- [ ] Test no reranker versus BGE and Qwen 0.6B rerankers only after the best hybrid baseline is frozen.
- [ ] Keep the least expensive pipeline that meets per-book gates.

**Gate:** Do not proceed to full generation evaluation until retrieval Recall@5 meets the target or every remaining miss has a documented ingestion/coverage cause.

## 8. Milestone 4: Complete backend behavior and Gemini validation

**Outcome:** The API returns stored, idempotent, correctly classified answers with server-resolved citations.

**Files:**

- Modify `backend/eduapp/app.py`, `generation.py`, `store.py`
- Create `backend/eduapp/schemas.py`, `services/`, and `providers/gemini.py`
- Create `backend/tests/api/`, `backend/tests/generation/`, and `backend/tests/security/`

**Tasks:**

- [ ] Correct and normalize all API response and error schemas to [Backend schema](BACKEND-SCHEMA.md).
- [ ] Separate domain services from route functions.
- [ ] Add stable safe error codes and a trace ID to errors.
- [ ] Enforce bounded history by both complete turns and tokens.
- [ ] Store normalized citations separately from answer JSON.
- [ ] Add a pending-message or distributed-lock-compatible concurrency model.
- [ ] Pin Gemini model and prompt version in every stored answer.
- [ ] Parse usage metadata and record billed token counts without logging content.
- [ ] Add one controlled repair for malformed model JSON only if total call budget permits.
- [ ] Test prompt injection embedded in evidence and conversation text.
- [ ] Confirm no provider credential is visible through OpenAPI, status, errors, or browser assets.

**Tests:** All route status codes, ownership failures, idempotent retries, conflicting IDs, rate limit, overload, provider timeout, quota failure, malformed response, invalid evidence ID, invalid quote, insufficient evidence, and clarification.

## 9. Milestone 5: Finish and inspect the student interface

**Outcome:** The responsive interface implements the full app flow and has been visually reviewed with real Bengali content.

**Files:**

- Refactor `apps/web/src/main.tsx` into feature components
- Refactor `apps/web/src/styles.css` into tokens and feature styles
- Create `apps/web/src/api/`, `features/study/`, `features/library/`, `features/evidence/`, and `features/preferences/`
- Create `apps/web/tests/`

**Tasks:**

- [ ] Resolve TypeScript and build failures from the initial single-file prototype.
- [ ] Replace framework response assumptions with typed API client schemas.
- [ ] Select the first ready book rather than always selecting the first book.
- [ ] Implement correct dialog focus trapping and trigger-focus restoration.
- [ ] Implement evidence overlay behavior for laptop and mobile widths.
- [ ] Add auto-scroll only when the reader is already near the newest message.
- [ ] Add source-unavailable behavior for expired saved answers.
- [ ] Convert repeated values into the token system in UIUX.md.
- [ ] Confirm every icon-only control has an accessible name and adequate target size.
- [ ] Render Bengali answers, long questions, lists, errors, empty states, and citations at representative widths.
- [ ] Remove or implement every control that does not yet perform its stated action.

**Verification:** TypeScript build, browser smoke tests, keyboard-only flow, screen-reader spot check, reduced motion, 320-pixel layout, 200% zoom, and screenshots at mobile/laptop/desktop sizes.

## 10. Milestone 6: End-to-end evaluation

**Outcome:** Quality, latency, cost, and failure reports support the release decision.

**Files:**

- Expand controlled `evals/` dataset to the PRD target
- Create versioned run manifests under ignored `artifacts/evaluations/`
- Add a public synthetic/sample report under `docs/evaluation/`

**Tasks:**

- [ ] Freeze the selected retrieval and generation configuration on validation data.
- [ ] Run no-context, gold-context, and actual-retrieval diagnostics.
- [ ] Score correctness, support, citation precision and coverage, abstention, language, latency, memory, and cost.
- [ ] Report all results per book and language with numerator and denominator.
- [ ] Categorize every failed test case by the earliest failing stage.
- [ ] Run the sealed test set once after configuration freeze.
- [ ] Manually verify the three assessment sample questions against the real source pages.

**Gate:** All TRD quality requirements pass or the release report explicitly blocks launch and identifies remediation.

## 11. Milestone 7: Production hardening and release

**Outcome:** A deployable application with secrets, persistence, recovery, and operations ready for real student use.

**Tasks:**

- [ ] Rotate all development credentials and configure separate staging and production secrets.
- [ ] Migrate SQLite to PostgreSQL using the production schema.
- [ ] Add pgvector and verify exact-result parity before considering HNSW.
- [ ] Replace in-memory limits and locks with shared production mechanisms.
- [ ] Add HTTPS, secure cookies, CSRF protection, strict CSP, allowed hosts/origins, and proxy-aware client-IP handling.
- [ ] Add structured redacted telemetry, dashboards, alerts, and cost limits.
- [ ] Containerize the API and web build using pinned base images.
- [ ] Add automated migrations, readiness checks, graceful shutdown, and rollback.
- [ ] Run dependency and secret scanning.
- [ ] Test backup and restore into a clean environment.
- [ ] Run the agreed 10-user load test and failure injection.
- [ ] Complete corpus redistribution and privacy review.

## 12. Test pyramid

| Layer | Focus | Provider/network behavior |
|---|---|---|
| Unit | Unicode tokenizer, RRF, chunking, validation, state transitions | No network |
| Component | SQLite/PostgreSQL repositories, index loading, Gemini parser | Stub provider |
| API integration | Ownership, idempotency, errors, citations, deletion | Stub provider, real test database |
| Retrieval evaluation | Real local embeddings and four indexes | Model downloads allowed; no Gemini required |
| Browser | Student flow, responsive behavior, accessibility | Stub API first, live API smoke second |
| End-to-end | Real question to real citation | Controlled Gemini project and approved books |
| Operational | Load, timeout, quota, crash, restore | Staging environment |

## 13. Definition of done

- Four approved source manifests and active indexes exist.
- The exact setup, ingestion, development, test, evaluation, and build commands succeed from a clean checkout.
- All deterministic tests pass with a stubbed provider.
- Real-provider smoke tests pass without exposing credentials.
- The bilingual evaluation meets the TRD gates per book.
- The UI has been inspected at mobile, laptop, and desktop sizes with real Bengali responses.
- Security, dependency, secret, load, failure, backup, and restore checks pass.
- Documentation reflects measured behavior and known corpus gaps.
- No step reports a hypothetical target as an achieved result.

## 14. Delivery risks

| Risk | Impact | Response |
|---|---|---|
| Legacy Bengali font mapping or scanned pages | Missing or corrupt evidence | Page-level visual audit and OCR/manual correction |
| HSC Second Paper syllabus mismatch | Confident answers from the wrong curriculum | Block “verified” status until contents mapping is complete |
| Four-book limit omits supplementary literature | Coverage gaps | Disclose scope and abstain; change corpus only through a product decision |
| Local Qwen model memory or dependency issues | Slow or failed indexing | Batch offline, use CPU fallback, compare BGE, document hardware |
| Gemini quota or model change | Answer outages | Stable provider adapter, safe errors, pinned IDs, measured alternative |
| Single-process locks and rate limits | Inconsistent multi-worker behavior | Replace before horizontal scaling |
| Weak Bengali evaluation labels | Misleading model selection | Bilingual review, grouped splits, adjudication, visible denominators |
