# Build verification — 11 September 2026

## Implemented in this build

- Fixed session and message INSERT statements so the database can persist chat turns.
- Enforced expiration for saved-answer retrieval and answer ownership checks.
- Added 17 regression tests covering persistence, duplicate requests, owner isolation, deletion cascades, expiry, API flow, malformed answers, source citation validation, and extraction fallback.
- Added an explicit Gemini JSON response schema. A live synthetic-evidence request passed schema and exact citation validation. This is an integration check, not a textbook accuracy evaluation.
- Added a pinned Python environment, Make targets, reproducible setup instructions, and an explicitly permitted esbuild install hook.
- Fixed frontend message IDs when a user edits a failed question before resubmitting.
- Added PDF auditing and resumable local Bengali/English OCR with per-page checkpoints and bounded workers. Original PDF bytes are preserved.

## Corpus findings

| Collection | PDF pages | Pages passing native Bengali extraction |
|---|---:|---:|
| SSC first paper | 265 | 0 |
| SSC second paper | 219 | 0 |
| HSC first paper | 350 | 0 |
| HSC second paper | 352 | 0 |

The HSC second-paper sample visually contains Bengali but extracts legacy-font character sequences. Tesseract recovered readable Bengali on PDF page 10; visual comparison also found transcription errors in headings and several words. Therefore OCR output requires review before corpus quality can be accepted. The length/script heuristic alone does not establish OCR accuracy.

Detailed source hashes, page flags, and extracted text are in ignored `data/audit/`. OCR checkpoints are in ignored `data/ocr/`. The four sources and syllabus caveats remain documented in [PDF sources](PDF-SOURCES.md).

## Verification evidence

- Historical backend verification: 17 tests passed; the current machine must recreate the Python 3.12 environment before this result is considered reproducible. Dependency deprecation warnings remain.
- Python package consistency: `pip check` reported no broken requirements.
- Gemini: one live structured-output check passed using synthetic evidence.
- Browser: study page rendered at desktop and 390-pixel mobile widths; library navigation and HSC filtering worked.
- Final frontend production build passed after the retry fix and dependency repair: 1,747 modules transformed, JavaScript bundle 379.33 kB (116.46 kB gzip).
- OCR sample preparation completed for 20 pages across all four books. Sample completion is not equivalent to transcription approval.
- Qwen model download was started; embedding verification and real index activation remain pending.

## Remaining release gates

1. Review OCR samples and improve transcription where needed.
2. Complete OCR for all four books and build versioned embedding indexes.
3. Run real Bengali/English questions with page-level evidence labels and measure retrieval/answer quality.
4. Complete keyboard, source-panel, and multi-turn browser checks on real indexed books.
5. Validate syllabus coverage, production ownership and rate limits, and deployment requirements.

Reference for local OCR setup: [Tesseract installation documentation](https://tesseract-ocr.github.io/tessdoc/Installation.html). Embedding implementation reference: [Qwen3-Embedding-0.6B model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B). Generator reference: [Gemini models](https://ai.google.dev/gemini-api/docs/models).

## Audit update — 20 September 2026

The current workspace audit confirmed that the Python source compiles, but it did not reproduce the historical test result on the active machine: the default interpreter is Python 3.9.6 and is missing the locked runtime dependencies. The lockfile targets Python 3.12, so test verification must be repeated inside the documented virtual environment.

The frontend has an existing `apps/web/dist` artifact, but a fresh `pnpm --dir apps/web build` reached Vite transformation and did not finish during the audit. Treat the previous build claim as historical until the build completes again.

No active files are present under `data/indexes/`. The four PDF sources, audit reports, and sample OCR checkpoints exist, but the Kaggle index ZIP has not yet been imported. The next implementation gate is therefore: finish the four-book OCR run, perform the accepted review sample, import the ZIP, and run retrieval evaluation before enabling textbook answers.

The following decisions are now accepted and recorded in `CONTEXT.md` and `docs/adr/`: the first release is four-book grounded QA; the pilot uses SQLite, NumPy, and BM25; activation requires the explicit OCR review gate; corpus artifacts remain private until rights are verified; and Gemini plus Qwen is the initial provider pair.
