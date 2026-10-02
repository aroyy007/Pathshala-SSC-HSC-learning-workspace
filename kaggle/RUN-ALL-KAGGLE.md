# Pathshala Kaggle notebook: SSC first, HSC second

This is the canonical cell-by-cell notebook sequence. It processes the two SSC books first, then the two HSC books, and finally builds one four-book index archive.

Use one private Kaggle dataset containing all four PDFs, with these exact filenames:

```text
ssc-2026-bangla-1.pdf
ssc-2026-bangla-2.pdf
hsc-2026-bangla-1.pdf
hsc-2026-bangla-2.pdf
```

Also attach the repository as a Kaggle dataset, or upload `kaggle/build_indexes.py` as a notebook input. The notebook does not need Gemini or Groq. The Qwen embedding model is downloaded from Hugging Face and usually does not need a token.

Enable a T4 GPU and Internet for the first run. Keep the PDFs, OCR checkpoints, and output ZIP private.

The indexer accepts a selected book without requiring the other books during that stage. This makes the SSC-first/HSC-second sequence resumable. The final `--stage index --book all` command still requires all four books and all 1,186 page checkpoints.

## Cell 1 — inspect the GPU

```bash
!nvidia-smi
```

## Cell 2 — install Bengali OCR fallback

```bash
!apt-get update -qq
!apt-get install -y -qq tesseract-ocr tesseract-ocr-ben
```

## Cell 3 — install normal index dependencies

```bash
!python -m pip install -q --upgrade-strategy only-if-needed pymupdf==1.26.4 "sentence-transformers>=5.1.1,<6.0.0" tqdm==4.67.1
```

Do not install PaddlePaddle into Kaggle's normal Python environment.

## Cell 4 — create the isolated PaddleOCR environment

```bash
!python -m pip install -q virtualenv
!python -m virtualenv --clear --system-site-packages /kaggle/working/paddle-env
!/kaggle/working/paddle-env/bin/python -m pip install -q --upgrade pip setuptools wheel wrapt
!/kaggle/working/paddle-env/bin/python -m pip install -q paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/
!/kaggle/working/paddle-env/bin/python -m pip install -q "paddleocr[doc-parser]>=3.6.0,<3.7.0" pymupdf==1.26.4 "numpy>=1.26,<3" tqdm==4.67.1
```

The `--system-site-packages` option avoids Kaggle's `sitecustomize`/`wrapt` startup problem while keeping Paddle dependencies isolated from the normal Torch environment.

## Cell 5 — verify both runtimes

```python
import subprocess
import torch

print("Torch:", torch.__version__)
print("Torch CUDA available:", torch.cuda.is_available())
assert torch.cuda.is_available(), "Enable a Kaggle GPU before continuing"

subprocess.run(
    [
        "/kaggle/working/paddle-env/bin/python",
        "-c",
        "import paddle; "
        "print('Paddle:', paddle.__version__); "
        "print('Paddle compiled with CUDA:', paddle.device.is_compiled_with_cuda()); "
        "print('Paddle device:', paddle.device.get_device()); "
        "assert paddle.device.is_compiled_with_cuda(); paddle.utils.run_check()",
    ],
    check=True,
)

print("Both runtimes are ready.")
```

## Cell 6 — copy the indexer into `/kaggle/working`

This cell finds the uploaded repository/script automatically. If it reports zero files, attach the repository dataset or upload `kaggle/build_indexes.py` to the notebook.

```python
from pathlib import Path
import shutil

candidates = [
    path for path in Path("/kaggle/input").rglob("build_indexes.py")
    if path.name == "build_indexes.py"
]

print("Indexer candidates:")
for path in candidates:
    print(" -", path)

assert candidates, (
    "No build_indexes.py found. Attach the Pathshala repository as a Kaggle "
    "dataset or upload kaggle/build_indexes.py."
)

source = next(
    (path for path in candidates if path.parent.name == "kaggle"),
    candidates[0],
)
shutil.copy2(source, "/kaggle/working/build_indexes.py")
print("Copied:", source)
```

## Cell 7 — verify all PDF inputs

```python
from pathlib import Path

BOOK_IDS = [
    "ssc-2026-bangla-1",
    "ssc-2026-bangla-2",
    "hsc-2026-bangla-1",
    "hsc-2026-bangla-2",
]

pdf_paths = {}
for book_id in BOOK_IDS:
    matches = list(Path("/kaggle/input").rglob(f"{book_id}.pdf"))
    print(book_id, matches)
    assert len(matches) == 1, f"Expected exactly one {book_id}.pdf"
    pdf_paths[book_id] = matches[0]

print("All four PDFs are ready.")
```

## Cell 8 — OCR SSC Bangla 1st Paper

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book ssc-2026-bangla-1 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

The command is resumable. If the cell stops, run the same cell again in the same Kaggle session.

## Cell 9 — OCR SSC Bangla 2nd Paper

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book ssc-2026-bangla-2 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

## Cell 10 — verify SSC OCR

```python
from pathlib import Path
import json
import pymupdf

ocr_root = Path("/kaggle/working/pathshala-build/ocr")
ssc_ids = ["ssc-2026-bangla-1", "ssc-2026-bangla-2"]

for book_id in ssc_ids:
    with pymupdf.open(pdf_paths[book_id]) as pdf:
        expected_pages = len(pdf)
    checkpoints = sorted((ocr_root / book_id).glob("*.json"))
    print(book_id, "checkpoints:", len(checkpoints), "expected:", expected_pages)
    assert len(checkpoints) == expected_pages, f"{book_id} OCR is incomplete"

    review = []
    for path in checkpoints:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "ok":
            review.append(record.get("page"))
    print(book_id, "automatically flagged pages:", review)

print("SSC OCR is complete. Expected combined SSC pages: 484.")
```

## Optional Cell 11 — save SSC checkpoints before leaving Kaggle

Run this only if the Kaggle runtime may stop before the HSC books finish. Download the ZIP from the notebook output and keep it private.

```python
import shutil

checkpoint_zip = shutil.make_archive(
    "/kaggle/working/ssc-ocr-checkpoints",
    "zip",
    root_dir="/kaggle/working/pathshala-build/ocr",
    base_dir=".",
)
print("Download:", checkpoint_zip)
```

If you start a fresh Kaggle session, attach that private checkpoint ZIP as an input and run this before the HSC commands:

```python
from pathlib import Path
import shutil

checkpoint_candidates = list(Path("/kaggle/input").rglob("ssc-ocr-checkpoints.zip"))
if checkpoint_candidates:
    restore_root = Path("/kaggle/working/pathshala-build/ocr")
    restore_root.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(checkpoint_candidates[0], restore_root, "zip")
    print("Restored SSC checkpoints from:", checkpoint_candidates[0])
else:
    print("No checkpoint ZIP found; start SSC OCR from Cell 8.")
```

## Cell 12 — OCR HSC Bangla 1st Paper

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book hsc-2026-bangla-1 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

## Cell 13 — OCR HSC Bangla 2nd Paper

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book hsc-2026-bangla-2 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

## Cell 14 — verify all OCR checkpoints

```python
from pathlib import Path
import json
import pymupdf

all_review = []
total = 0
for book_id in BOOK_IDS:
    with pymupdf.open(pdf_paths[book_id]) as pdf:
        expected_pages = len(pdf)
    checkpoints = sorted((ocr_root / book_id).glob("*.json"))
    print(book_id, "checkpoints:", len(checkpoints), "expected:", expected_pages)
    assert len(checkpoints) == expected_pages, f"{book_id} OCR is incomplete"
    total += len(checkpoints)
    for path in checkpoints:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "ok":
            all_review.append((book_id, record.get("page")))

print("Total OCR checkpoints:", total, "expected: 1186")
print("Automatically flagged pages:", all_review)
assert total == 1186, "OCR is incomplete; rerun the missing book cell"
```

## Cell 15 — build all four Qwen indexes

Run this only after Cell 14 reports 1,186 checkpoints. This is the only embedding/package stage needed for the final archive.

```bash
!python /kaggle/working/build_indexes.py --stage index --book all --ocr-engine paddle-vl --ocr-workers 1 --embed-batch-size 16 --dpi 250
```

Successful indexing ends with `READY: /kaggle/working/pathshala-indexes.zip`.

## Cell 16 — validate and download the final archive

```python
from pathlib import Path
from IPython.display import FileLink, display
import json
import zipfile

archive = Path("/kaggle/working/pathshala-indexes.zip")
summary = Path("/kaggle/working/pathshala-indexes/build-summary.json")

assert archive.is_file(), "Output ZIP was not created; inspect Cell 15"
assert zipfile.is_zipfile(archive), "Output is not a ZIP"

with zipfile.ZipFile(archive) as bundle:
    bad = bundle.testzip()
    assert bad is None, f"Corrupt ZIP entry: {bad}"
    names = bundle.namelist()
    for book_id in BOOK_IDS:
        assert any(f"indexes/{book_id}/active.json" in name for name in names), (
            f"Missing {book_id} from the final archive"
        )
    print("ZIP entries:", len(names))

print(json.dumps(json.loads(summary.read_text()), indent=2, ensure_ascii=False))
print(f"ZIP size: {archive.stat().st_size / 1024**2:.1f} MB")
display(FileLink(str(archive)))
```

## After Kaggle

Download the final ZIP privately and import it from the repository root:

```bash
.venv/bin/python scripts/import_kaggle_indexes.py \
  /absolute/path/pathshala-indexes.zip
```

The importer intentionally refuses unreviewed output. Review flagged pages, 20 clean pages per book, chapter boundaries, and sample-answer pages before release activation. Use `--activate-unreviewed` only for local development.

## OKF integration boundary

OKF is optional for this pipeline. Use it later for a curated concept bundle such as chapter summaries, grammar rules, aliases, learning objectives, reviewed explanations, and links to evidence pages. Do not convert raw OCR into trusted OKF concepts automatically, and do not replace the PDF index with OKF: the PDF/OCR manifest remains the source evidence and OKF becomes a human-reviewed navigation/teaching layer.
