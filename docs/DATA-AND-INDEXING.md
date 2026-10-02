# Data and indexing

## Data classification

| Artifact | Classification | Git policy |
| --- | --- | --- |
| Source PDFs | Private source material | Never commit by default |
| OCR page JSON | Private derived text | Never commit |
| Embedding model cache | Large private dependency cache | Never commit |
| Vector/chunk index ZIP | Private derived corpus | Never commit or publish without rights |
| Evaluation labels | Review-controlled project data | Keep private when source text is protected |
| Code and schemas | Project source | Commit after review |
| API keys | Secret | `.env` or deployment secret store only |

## Four collections

```text
ssc-2026-bangla-1
ssc-2026-bangla-2
hsc-2026-bangla-1
hsc-2026-bangla-2
```

Every collection has a separate source hash, page list, chunk list, vector matrix, quality report, and active manifest. A session never searches more than its selected collection/version.

## Pipeline

1. Verify the input filename, PDF signature, page count, encryption state, byte size, and SHA-256.
2. Prefer native PDF extraction when the page contains usable Bengali text.
3. Render flagged pages and run PaddleOCR-VL in Kaggle, with Tesseract Bengali/English fallback.
4. Normalize Unicode without destroying Bengali combining marks; retain `raw_text`, method, page number, and quality status.
5. Exclude pages marked `review` from retrieval until a reviewer accepts or corrects them.
6. Create deterministic page-scoped sentence-aware chunks with token limits and stable IDs.
7. Encode chunks with Qwen3-Embedding-0.6B and store normalized vectors.
8. Write the immutable manifest, quality report, active pointer, and ZIP archive.
9. Review the required OCR sample and import through `scripts/import_kaggle_indexes.py`.

## Index layout

```text
data/indexes/{book_id}/
├── active.json
├── quality.json
└── {version}/
    ├── chunks.json
    ├── manifest.json
    ├── pages.json
    ├── source.pdf
    └── vectors.npy
```

`manifest.json` binds the book ID, source hash, pipeline/settings, page and chunk counts, vector dimensions, model ID, and review status. `active.json` is replaced atomically after a complete build. A failed build must never replace the last valid active pointer.

## Review gate

The accepted release gate is:

- Every automatically flagged page is reviewed.
- At least 20 automatically clean pages per book are compared with the rendered PDF.
- Chapter boundaries and the pages supporting the supplied sample questions are checked.
- Chunk/page mappings and Bengali names are inspected.
- Retrieval labels are created for the evaluation set.
- The manifest is marked reviewed only through a controlled workflow.

`--activate-unreviewed` exists only for local development and must not be used for a production release.

## Import

```bash
.venv/bin/python scripts/import_kaggle_indexes.py \
  /absolute/path/pathshala-indexes.zip
```

The importer validates archive paths, file sizes, source hashes, vector shapes, finite values, manifest equality, page mappings, chunk IDs, and the exact set of four collections. It refuses to overwrite an existing collection directory.

## Rebuilding

Changing any source PDF, OCR output, chunking setting, pipeline version, or embedding model creates a new corpus version. Never edit an active index in place. Rebuild, validate, review, then atomically activate the new version.
