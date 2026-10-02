# Kaggle GPU indexing runbook

`RUN-ALL-KAGGLE.md` is the canonical copy-paste notebook sequence. This page explains the inputs, privacy boundary, and import handoff; use the linked runbook for the current isolated PaddleOCR environment and resumable one-book commands.

## Expected time

The corpus has 1,186 PDF pages. OCR is the long stage and uses the GPU-backed PaddleOCR process plus CPU rendering; Qwen embedding uses the GPU. A first run can exceed a Kaggle session limit, especially when the PaddleOCR model must be downloaded. The pipeline checkpoints every OCR page, so the four books should be run as separate resumable jobs when a single session is not long enough.

## Prepare the Kaggle notebook

1. Create a private Kaggle dataset containing these exact filenames:
   - `ssc-2026-bangla-1.pdf`
   - `ssc-2026-bangla-2.pdf`
   - `hsc-2026-bangla-1.pdf`
   - `hsc-2026-bangla-2.pdf`
2. Attach that dataset and this repository (or upload `build_indexes.py`).
3. Enable a GPU accelerator. Enable Internet for the initial model/package download.
4. Do not put Gemini or Hugging Face keys in notebook cells. Qwen3-Embedding-0.6B is public and normally needs no token.

For the exact cell-by-cell sequence, open [RUN-ALL-KAGGLE.md](RUN-ALL-KAGGLE.md). The older compact command below is suitable only when the runtime and installed OCR environment are already known to work.

Run these notebook cells:

```bash
!apt-get update -qq
!apt-get install -y -qq tesseract-ocr tesseract-ocr-ben
!pip install -q -r /kaggle/input/REPOSITORY_DATASET/kaggle/requirements.txt
```

Replace `REPOSITORY_DATASET` with the attached repository dataset directory shown under `/kaggle/input`.

```bash
!python /kaggle/input/REPOSITORY_DATASET/kaggle/build_indexes.py --book all --ocr-workers 2 --embed-batch-size 32
```

For a T4 GPU, start with batch size 32. Reduce it to 16 or 8 after a CUDA out-of-memory error. Increasing OCR workers above the Kaggle CPU allocation usually makes the run slower.

## Download and import

Download `/kaggle/working/pathshala-indexes.zip` from Notebook Output. Keep the ZIP private because it includes the source PDFs and OCR text. Place it anywhere locally and validate/import it with:

```bash
.venv/bin/python scripts/import_kaggle_indexes.py /absolute/path/pathshala-indexes.zip
```

The importer validates paths, sizes, source hashes, manifests, vector shapes, finite values, chunk IDs and page mappings. It refuses to activate unreviewed output and refuses to overwrite an existing book directory. For development after you have inspected the OCR samples, explicitly use `--activate-unreviewed`; this flag does not change the manifest's review status.

Before treating an index as production-ready:

1. Compare at least 20 OCR pages per book with the rendered PDF.
2. Record corrections or exclusions.
3. Set `manual_review_complete` only through a reviewed import workflow; do not hand-edit manifests merely to bypass the gate.
4. Run `make test`, `make evaluate DATASET=...`, and real Bengali/English question checks.

The generated shape is directly compatible with the current backend:

```text
indexes/
└── {book_id}/
    ├── active.json
    ├── quality.json
    └── {version}/
        ├── chunks.json
        ├── manifest.json
        ├── pages.json
        ├── source.pdf
        └── vectors.npy
```
