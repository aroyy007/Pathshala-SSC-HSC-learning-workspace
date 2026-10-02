# Kaggle copy/paste cells

For a two-session run, use [01_ssc_books.ipynb](01_ssc_books.ipynb) and then
[02_hsc_books_and_final_index.ipynb](02_hsc_books_and_final_index.ipynb). The
complete copy/paste reference remains [RUN-ALL-KAGGLE.md](RUN-ALL-KAGGLE.md).

That notebook keeps PaddleOCR and PyTorch in separate environments and includes
the Kaggle `sitecustomize`/`wrapt` fix. Older instructions that installed
PaddlePaddle directly into Kaggle's normal Python environment are unsafe because
Paddle and the preinstalled PyTorch stack can require different NVIDIA packages.

Upload one private Kaggle dataset containing exactly these four files:

```text
ssc-2026-bangla-1.pdf
ssc-2026-bangla-2.pdf
hsc-2026-bangla-1.pdf
hsc-2026-bangla-2.pdf
```

The current indexer source to paste into the notebook is
[build_indexes.py](build_indexes.py).
