# Implementation backlog

This backlog began as the build sequence for `PRD.md`. The React/FastAPI foundation, ingestion pipeline, tests and a live synthetic-evidence Gemini check now exist. Corpus retrieval evaluation has not run. The version 2 roadmap in `IMPLEMENTATION-PLAN.md` supersedes this file for board questions, solutions, notebook, audio and video work.

## Version 2 backlog entry points

1. Complete Kaggle OCR/index generation and reviewed import for the four textbooks.
2. Freeze the curriculum taxonomy and source-rights registry.
3. Ingest one reviewed board-question slice with structured filters.
4. Implement attempts, hints, rubrics and reviewed easy solutions.
5. Add notebook/progress ownership and retention.
6. Benchmark Bengali TTS and deliver transcript-linked audio.
7. Add deterministic narrated-slide video with captions and citations.

## Expanded scope dependency

Apply PRD section 2.1 throughout: four paper collections, mandatory collection selection, source applicability verification, per-collection readiness, and session/index isolation. Build collection routing into the first ingestion/database/API slice. Add tests proving identical keywords cannot leak evidence from another level or paper. Treat 2nd Paper rule application as a distinct evaluated behavior. The original task sequence below applies to each collection, with shared pipeline code.

## 1. Establish the corpus boundary

Create `configs/corpus.yaml`, `src/eduapp/ingestion/manifest.py`, and `scripts/ingest.py`. The manifest owns the exact PDF hash, source metadata, and extraction configuration. Keep secrets out of it.

Interface: `inspect_pdf(path: Path) -> DocumentManifest`. A manifest includes source SHA-256, page count, title, and version ID. Reject malformed PDFs and configured resource-limit violations. An encrypted document returns a documented unsupported-input error unless authorized credentials are provided.

Verification: a valid small fixture is identified consistently; a renamed identical PDF has the same content identity; a changed PDF creates a new version. Read the exact assigned book and record the representative-page inspection before selecting OCR settings.

## 2. Preserve evidence through extraction

Create `src/eduapp/ingestion/extract.py`, `normalize.py`, `quality.py`, and `tests/ingestion/test_evidence_mapping.py`.

Interfaces: `extract_pages(manifest) -> list[PageRecord]`, `normalize_page(page) -> CanonicalPage`. Each canonical span retains its source page/block reference. OCR stores method and quality flags alongside text.

Verification: fixtures cover Bengali combining marks, printed/PDF page mismatch, repeated headers, and two-column ordering. A quote selected from canonical text maps back to the correct page. Native extraction is preferred when accurate; OCR is used for the pages that actually need it. Produce a transcription-based quality report rather than asserting visual quality from token count.

## 3. Build immutable chunks and dense retrieval

Create `src/eduapp/ingestion/chunk.py`, `src/eduapp/storage/`, `src/eduapp/retrieval/dense.py`, and initial database migrations.

Interfaces: `chunk_pages(pages, config) -> list[Chunk]`, `embed_chunks(chunks, model_revision) -> EmbeddingBatch`, `search_dense(query, index_version, limit) -> list[Candidate]`. Candidates carry chunk ID, score, retriever name, and rank.

Verification: no chunk crosses a work boundary; long paragraphs respect tokenizer limits; re-ingestion is idempotent; invalid dimensions fail before insert; exact-search results match a small hand-computed vector fixture. Confirm both Bengali and English can retrieve the source span for a reviewed fact without generation.

## 4. Deliver one grounded answer

Create `src/eduapp/generation/provider.py`, `prompts.py`, `validate.py`, and `src/eduapp/pipeline.py`.

Interfaces: `retrieve(question, session_context, version) -> EvidenceBundle`, `generate(question, language, evidence) -> DraftAnswer`, `validate_answer(draft, evidence) -> AnswerResult`. Provider-specific response types do not leak into API schemas.

Verification: a fabricated citation ID is rejected; a quotation from another passage is rejected; missing evidence yields the explicit no-answer status; a provider timeout yields an infrastructure error. Test a generator with correct gold evidence separately from actual retrieval. Manually inspect the original sample cases with real page citations.

## 5. Add lexical fusion only after a baseline

Create `src/eduapp/retrieval/tokenize.py`, `bm25.py`, `fusion.py`, and optional `rerank.py`.

Interfaces: `tokenize_search(text) -> list[str]`, `search_bm25(query, artifact, limit) -> list[Candidate]`, `fuse(rankings, k=60) -> list[Candidate]`, `rerank(query, candidates) -> list[Candidate]`.

Verification: tokenization preserves Bengali marks; absent RRF entries contribute zero; score ties are deterministic; artifact and vector versions cannot diverge. Compare dense-only, lexical-only, hybrid, and reranked variants using identical gold cases. Keep the simplest configuration that meets the quality gates within the latency budget.

## 6. Add sessions and contracts

Create `src/eduapp/conversations/service.py`, `resolve.py`, and `src/eduapp/api/`.

Interfaces: `create_session(owner) -> Session`, `answer_message(owner, session_id, client_message_id, text, language) -> AnswerResult`, `reset_session(owner, session_id) -> None`.

Verification: follow-up references resolve when unambiguous, unclear references produce clarification, reset removes context, another owner cannot read messages, two concurrent messages cannot corrupt ordering, retries do not create duplicate answers, and retired-version citations remain available to their owning sessions.

## 7. Build the reading interface

Create `apps/web/src/features/chat/`, `features/evidence/`, and `features/settings/`. Use the PRD's layout and language-safe typography; confirm final colors and type rendering in-browser.

Verification: submit by keyboard, switch answer language, inspect a citation, return focus after closing evidence, retry an error without duplicate messages, reset a session, use a narrow mobile viewport, and read at 200% zoom. Confirm glyphs and line-height with the actual Bengali strings. Add Playwright tests for these user-visible flows.

## 8. Make evaluation reproducible

Create `src/eduapp/evaluation/dataset.py`, `metrics.py`, `run.py`, and `scripts/evaluate.py`. Store public screenshot examples separately from sealed test groups.

Interface: `evaluate(dataset, pipeline_config, run_manifest) -> EvaluationReport`. Reports preserve every per-example outcome, including failures, and contain dataset hash, corpus hash, code SHA, model/prompt revisions, costs, and hardware profile.

Verification: metric fixtures cover missing evidence, multi-evidence recall versus hit rate, approved numeral aliases, zero denominators, abstention on answerables, and invalid citations. Ensure all variants of a semantic group share one split. No gold-label files appear in the corpus ingestion source list.

## 9. Rehearse failure and recovery

Implement the atomic index activation and process readiness checks. Add a bounded queue for expensive inference and respect the overall request deadline.

Verification: kill ingestion before activation and confirm the prior index remains served; start a worker with a mismatched lexical artifact and confirm readiness fails; simulate provider timeout and retry; restore database and artifacts into a clean environment. Run the agreed 10-user warm-load test and report queue time, stage times, errors, and memory.

## 10. Package actual evidence

Write the runtime README only after setup and commands have been exercised. Include environment-variable names without secrets, exact installation commands, ingestion instructions, API requests, bilingual real outputs, evaluation results, and observed limitations.

Proposed command interface to implement:

```text
python scripts/ingest.py --config configs/corpus.yaml
python scripts/evaluate.py --split validation --config configs/pipeline.yaml
python scripts/evaluate.py --split test --config configs/release.yaml
pytest
npm --prefix apps/web run build
npm --prefix apps/web run test:e2e
```

The final test command is run only after validation-based selection freezes the release configuration. Do not claim these commands work before they exist and pass. Public submission is a later action, after the local deliverable is complete and the user authorizes publication.
