# Pathshala Kaggle notebook: clean Run All sequence

Use a new Kaggle session. Attach one private dataset containing only the four PDFs, enable a T4 GPU and Internet, and add the following cells in exactly this order. PaddleOCR and PyTorch use separate Python environments so their CUDA dependencies cannot replace each other.

## Cell 1 — inspect the GPU

```bash
!nvidia-smi
```

## Cell 2 — install system OCR fallback

```bash
!apt-get update -qq
!apt-get install -y -qq tesseract-ocr tesseract-ocr-ben
```

## Cell 3 — install index dependencies in Kaggle's normal environment

```bash
!python -m pip install -q --upgrade-strategy only-if-needed pymupdf==1.26.4 "sentence-transformers>=5.1.1,<6.0.0" tqdm==4.67.1
```

Do not install PaddlePaddle into the normal Kaggle environment.

## Cell 4 — create a Kaggle-safe isolated PaddleOCR environment

```bash
!python -m pip install -q virtualenv
!python -m virtualenv --clear --system-site-packages /kaggle/working/paddle-env
!/kaggle/working/paddle-env/bin/python -m pip install -q --upgrade pip setuptools wheel wrapt
!/kaggle/working/paddle-env/bin/python -m pip install -q paddlepaddle-gpu==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu130/
!/kaggle/working/paddle-env/bin/python -m pip install -q "paddleocr[doc-parser]>=3.6.0,<3.7.0" pymupdf==1.26.4 "numpy>=1.26,<3" tqdm==4.67.1
```

Kaggle's global `sitecustomize` imports `wrapt` while Python starts. A standard
`venv` does not initially contain that package, so `ensurepip` can fail before
the environment has a working `pip`. `virtualenv --system-site-packages` lets
the new interpreter start using Kaggle's existing support packages; Paddle and
its CUDA libraries are still installed under `/kaggle/working/paddle-env`.

## Cell 5 — verify both environments

```python
import subprocess
import torch

print("Torch:", torch.__version__)
print("Torch CUDA:", torch.cuda.is_available())
assert torch.cuda.is_available()

subprocess.run(
    [
        "/kaggle/working/paddle-env/bin/python",
        "-c",
        "import paddle; print('Paddle:', paddle.__version__); "
        "print('Paddle CUDA:', paddle.device.is_compiled_with_cuda()); "
        "print('Paddle device:', paddle.device.get_device()); "
        "assert paddle.device.is_compiled_with_cuda(); paddle.utils.run_check()",
    ],
    check=True,
)

print("Both environments are ready. Continue to Cell 6.")
```

Do not continue if this cell raises an exception or does not report that
PaddlePaddle was installed successfully.

## Cell 6 — write the current indexer

Create a code cell beginning with this line and paste the complete contents of `kaggle/build_indexes.py` below it:

```python
%%writefile /kaggle/working/build_indexes.py
```

## Cell 7 — verify the four PDF inputs

```python
from pathlib import Path

expected = [
    "ssc-2026-bangla-1.pdf",
    "ssc-2026-bangla-2.pdf",
    "hsc-2026-bangla-1.pdf",
    "hsc-2026-bangla-2.pdf",
]

for filename in expected:
    matches = list(Path("/kaggle/input").rglob(filename))
    print(filename, matches)
    assert len(matches) == 1, f"Expected exactly one {filename}"

print("All four PDFs are ready.")
```

## Cell 8 — OCR all books in the isolated Paddle environment

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book all --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

Successful OCR ends with `OCR_READY: 1186 page checkpoints`.

If Kaggle stops before `OCR_READY`, the run usually hit the notebook time limit.
The completed pages are safe in `/kaggle/working/pathshala-build/ocr` for the
current session. Rerun the same cell to resume; existing page checkpoints are
skipped automatically.

For long runs, use these four OCR cells instead of the single all-book OCR cell:

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book ssc-2026-bangla-1 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book ssc-2026-bangla-2 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book hsc-2026-bangla-1 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

```bash
!PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True /kaggle/working/paddle-env/bin/python /kaggle/working/build_indexes.py --stage ocr --book hsc-2026-bangla-2 --ocr-engine paddle-vl --ocr-workers 1 --dpi 250
```

Each command can be run again safely. The script reads already-created page
JSON files and continues from the missing pages.

## Cell 9 — verify OCR checkpoints

```python
from pathlib import Path
import json

ocr_root = Path("/kaggle/working/pathshala-build/ocr")
checkpoints = sorted(ocr_root.rglob("*.json"))
print("OCR checkpoints:", len(checkpoints))
assert len(checkpoints) == 1186, "OCR is incomplete; rerun Cell 8 to resume."

review = []
for path in checkpoints:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["status"] != "ok":
        review.append((path.parent.name, record["page"]))

print("Automatically flagged pages:", review)
```

## Cell 10 — build Qwen embeddings and package the indexes

```bash
!python /kaggle/working/build_indexes.py --stage index --book all --ocr-engine paddle-vl --ocr-workers 1 --embed-batch-size 16 --dpi 250
```

Successful indexing ends with `READY: /kaggle/working/pathshala-indexes.zip`.

## Cell 11 — validate and download

```python
from pathlib import Path
from IPython.display import FileLink, display
import json
import zipfile

archive = Path("/kaggle/working/pathshala-indexes.zip")
summary = Path("/kaggle/working/pathshala-indexes/build-summary.json")

assert archive.is_file(), "Output ZIP was not created; inspect Cell 10."
assert zipfile.is_zipfile(archive), "Output is not a ZIP."

with zipfile.ZipFile(archive) as bundle:
    bad = bundle.testzip()
    assert bad is None, f"Corrupt entry: {bad}"
    print("ZIP entries:", len(bundle.namelist()))

print(json.dumps(json.loads(summary.read_text()), indent=2, ensure_ascii=False))
print(f"ZIP size: {archive.stat().st_size / 1024**2:.1f} MB")
display(FileLink(str(archive)))
```

The downloadable output is `/kaggle/working/pathshala-indexes.zip`.
