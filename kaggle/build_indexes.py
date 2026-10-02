"""Build Pathshala's four textbook indexes in a Kaggle notebook.

Input: four PDFs in any attached Kaggle dataset, named exactly as BOOKS below.
Output: /kaggle/working/pathshala-indexes.zip, compatible with data/indexes/.

PaddleOCR-VL and Qwen embeddings use the Kaggle GPU. Tesseract remains a
per-page fallback. Page checkpoints make reruns resumable inside one notebook
session. Persist the working directory as a Kaggle output to resume later.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pymupdf
from tqdm.auto import tqdm

BOOKS = {
    "ssc-2026-bangla-1": {"level": "SSC", "paper": 1, "title": "বাংলা সাহিত্য"},
    "ssc-2026-bangla-2": {"level": "SSC", "paper": 2, "title": "বাংলা ব্যাকরণ"},
    "hsc-2026-bangla-1": {"level": "HSC", "paper": 1, "title": "সাহিত্যপাঠ"},
    "hsc-2026-bangla-2": {"level": "HSC", "paper": 2, "title": "বাংলা দ্বিতীয় পত্র"},
}
BOOK_GROUPS = {
    "ssc": ["ssc-2026-bangla-1", "ssc-2026-bangla-2"],
    "hsc": ["hsc-2026-bangla-1", "hsc-2026-bangla-2"],
}
MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
PADDLE_OCR_VERSION = "v1.6"
PIPELINE_VERSION = "kaggle-paddle-vl-tesseract-page-sentence-v2"
INPUT_ROOT = Path("/kaggle/input")
WORK_ROOT = Path("/kaggle/working/pathshala-build")
OUTPUT_ROOT = Path("/kaggle/working/pathshala-indexes")


@dataclass(frozen=True)
class Settings:
    dpi: int = 250
    ocr_workers: int = 2
    embed_batch_size: int = 32
    max_tokens: int = 350
    overlap_tokens: int = 50
    minimum_bengali_chars: int = 20
    minimum_text_chars: int = 60


class PaddleVLOcr:
    """GPU document OCR with a Tesseract fallback handled by ``ocr_page``."""

    name = f"paddleocr-vl-{PADDLE_OCR_VERSION}"

    def __init__(self) -> None:
        try:
            from paddleocr import PaddleOCRVL
        except ImportError as exc:
            raise RuntimeError(
                "Install paddlepaddle-gpu and paddleocr[doc-parser] from the v2 runbook"
            ) from exc
        try:
            self.pipeline = PaddleOCRVL(
                pipeline_version=PADDLE_OCR_VERSION,
                device="gpu:0",
            )
        except TypeError:
            self.pipeline = PaddleOCRVL(pipeline_version=PADDLE_OCR_VERSION)

    def recognize(self, image_path: Path) -> str:
        with tempfile.TemporaryDirectory(prefix="paddle-result-") as scratch:
            result_dir = Path(scratch)
            results = list(self.pipeline.predict(str(image_path)))
            for result in results:
                result.save_to_markdown(save_path=str(result_dir))
            markdown = []
            for output in sorted(result_dir.rglob("*.md")):
                markdown.append(output.read_text(encoding="utf-8", errors="replace"))
            text = "\n".join(markdown)
            text = re.sub(r"!\[[^]]*]\([^)]*\)", "", text)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
            return normalize(text)

    def close(self) -> None:
        del self.pipeline
        gc.collect()


class TesseractOcr:
    name = "tesseract-ben-eng"

    def recognize(self, image_path: Path) -> str:
        process = subprocess.run(
            ["tesseract", str(image_path), "stdout", "-l", "ben+eng", "--psm", "3"],
            capture_output=True,
            text=True,
            timeout=180,
            env=os.environ | {"OMP_THREAD_LIMIT": "1"},
        )
        if process.returncode:
            raise RuntimeError(f"Tesseract failed: {process.stderr[-300:]}")
        return normalize(process.stdout)

    def close(self) -> None:
        return None


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u00ad", "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def bengali_chars(text: str) -> int:
    return sum("\u0980" <= char <= "\u09ff" for char in text)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locate_pdfs(book_ids: list[str]) -> dict[str, Path]:
    located = {}
    for book_id in book_ids:
        matches = list(INPUT_ROOT.rglob(f"{book_id}.pdf"))
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one {book_id}.pdf under {INPUT_ROOT}; found {len(matches)}"
            )
        if matches[0].stat().st_size > 100 * 1024 * 1024:
            raise RuntimeError(f"{matches[0].name} exceeds the 100 MB input limit")
        with matches[0].open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise RuntimeError(f"{matches[0].name} is not a PDF")
        located[book_id] = matches[0]
    return located


def check_ocr() -> str:
    binary = shutil.which("tesseract")
    if not binary:
        raise RuntimeError("Tesseract is missing; run the setup cell in kaggle/README.md")
    languages = subprocess.run(
        [binary, "--list-langs"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    if "ben" not in languages or "eng" not in languages:
        raise RuntimeError("Tesseract Bengali and English language data are required")
    return subprocess.run(
        [binary, "--version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]


def native_page_text(pdf_path: Path, page_index: int) -> str:
    with pymupdf.open(pdf_path) as pdf:
        return normalize(pdf[page_index].get_text("text", sort=True))


def ocr_page(
    pdf_path: Path,
    page_index: int,
    cache_dir: Path,
    source_hash: str,
    settings: Settings,
    tesseract_version: str,
    primary_ocr,
    cache_only: bool = False,
) -> dict:
    checkpoint = cache_dir / f"{page_index + 1:04d}.json"
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if (
            saved.get("source_sha256") == source_hash
            and saved.get("pipeline") == PIPELINE_VERSION
            and saved.get("primary_ocr") == primary_ocr.name
        ):
            return saved
    if cache_only:
        raise RuntimeError(
            f"Missing valid PaddleOCR checkpoint for {pdf_path.name} page {page_index + 1}. "
            "Run --stage ocr first."
        )

    raw_text = native_page_text(pdf_path, page_index)
    text = raw_text
    method = "native"
    candidates = {}
    if len(text) < settings.minimum_text_chars or bengali_chars(text) < settings.minimum_bengali_chars:
        with tempfile.TemporaryDirectory(prefix="ocr-") as scratch:
            image_path = Path(scratch) / "page.png"
            with pymupdf.open(pdf_path) as pdf:
                colorspace = (
                    pymupdf.csRGB
                    if primary_ocr.name.startswith("paddleocr-vl")
                    else pymupdf.csGRAY
                )
                pixmap = pdf[page_index].get_pixmap(
                    dpi=settings.dpi, colorspace=colorspace, alpha=False
                )
                pixmap.save(image_path)
            try:
                primary_text = primary_ocr.recognize(image_path)
            except Exception as exc:
                print(
                    f"Primary OCR failed for {pdf_path.name} page {page_index + 1}: "
                    f"{type(exc).__name__}"
                )
                primary_text = ""
            candidates[primary_ocr.name] = primary_text
            text = primary_text
            method = primary_ocr.name
            if (
                len(text) < settings.minimum_text_chars
                or bengali_chars(text) < settings.minimum_bengali_chars
            ) and primary_ocr.name != "tesseract-ben-eng":
                fallback = TesseractOcr().recognize(image_path)
                candidates["tesseract-ben-eng"] = fallback
                text = fallback
                method = "tesseract-ben-eng-fallback"

    record = {
        "page": page_index + 1,
        "text": text,
        "raw_text": raw_text,
        "method": method,
        "status": "ok"
        if len(text) >= settings.minimum_text_chars
        and bengali_chars(text) >= settings.minimum_bengali_chars
        else "review",
        "bengali_characters": bengali_chars(text),
        "source_sha256": source_hash,
        "pipeline": PIPELINE_VERSION,
        "primary_ocr": primary_ocr.name,
        "ocr_candidates": {
            name: {
                "characters": len(value),
                "bengali_characters": bengali_chars(value),
            }
            for name, value in candidates.items()
        },
        "tesseract": tesseract_version,
    }
    temporary = checkpoint.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False))
    os.replace(temporary, checkpoint)
    return record


def extract_book(
    book_id: str,
    pdf_path: Path,
    settings: Settings,
    tesseract_version: str,
    primary_ocr,
    cache_only: bool = False,
) -> tuple[str, list[dict]]:
    source_hash = sha256_file(pdf_path)
    cache = WORK_ROOT / "ocr" / book_id
    cache.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf_path) as pdf:
        page_count = len(pdf)
        if not 1 <= page_count <= 1000 or pdf.is_encrypted:
            raise RuntimeError(f"Unsupported page count or encryption in {pdf_path.name}")

    def process(page_index: int) -> dict:
        return ocr_page(
            pdf_path,
            page_index,
            cache,
            source_hash,
            settings,
            tesseract_version,
            primary_ocr,
            cache_only,
        )

    with ThreadPoolExecutor(max_workers=settings.ocr_workers) as executor:
        pages = list(
            tqdm(
                executor.map(process, range(page_count)),
                total=page_count,
                desc=f"OCR {book_id}",
            )
        )
    pages.sort(key=lambda item: item["page"])
    return source_hash, pages


def chunk_pages(
    book_id: str,
    source_hash: str,
    pages: list[dict],
    tokenizer,
    settings: Settings,
) -> list[dict]:
    chunks = []
    book = BOOKS[book_id]
    for page in pages:
        if page["status"] != "ok":
            continue
        units = [
            value.strip()
            for value in re.split(r"(?<=[।!?])\s+|\n\s*\n", page["text"])
            if value.strip()
        ]
        window: list[int] = []
        window_index = 0
        for unit in units:
            unit_ids = tokenizer.encode(unit, add_special_tokens=False)
            if window and len(window) + len(unit_ids) > settings.max_tokens:
                decoded = normalize(tokenizer.decode(window, skip_special_tokens=True))
                add_chunk(chunks, book_id, book, source_hash, page["page"], window_index, decoded)
                window_index += 1
                window = window[-settings.overlap_tokens :]
            for start in range(0, len(unit_ids), settings.max_tokens):
                part = unit_ids[start : start + settings.max_tokens]
                if window and len(window) + len(part) > settings.max_tokens:
                    decoded = normalize(tokenizer.decode(window, skip_special_tokens=True))
                    add_chunk(chunks, book_id, book, source_hash, page["page"], window_index, decoded)
                    window_index += 1
                    window = window[-settings.overlap_tokens :]
                window.extend(part)
        if window:
            decoded = normalize(tokenizer.decode(window, skip_special_tokens=True))
            add_chunk(chunks, book_id, book, source_hash, page["page"], window_index, decoded)
    return chunks


def add_chunk(chunks, book_id, book, source_hash, page, position, text):
    if len(text) < 20:
        return
    chunk_id = hashlib.sha256(
        f"{source_hash}:{page}:{position}:{text}".encode()
    ).hexdigest()[:24]
    context = f'{book["level"]} Bangla Paper {book["paper"]} | {book["title"]}'
    chunks.append(
        {
            "id": chunk_id,
            "book_id": book_id,
            "page": page,
            "text": text,
            "search_text": f"{context}\n{text}",
        }
    )


def embed_chunks(model, chunks: list[dict], settings: Settings) -> np.ndarray:
    vectors = model.encode(
        [item["search_text"] for item in chunks],
        batch_size=settings.embed_batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True,
    ).astype(np.float32)
    if len(vectors) != len(chunks) or not np.isfinite(vectors).all():
        raise RuntimeError("Embedding validation failed")
    return vectors


def write_index(book_id, pdf_path, source_hash, pages, chunks, vectors, settings):
    page_hash = hashlib.sha256(
        json.dumps(pages, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()
    version = hashlib.sha256(
        f"{source_hash}:{page_hash}:{MODEL_ID}:{PIPELINE_VERSION}".encode()
    ).hexdigest()[:20]
    base = OUTPUT_ROOT / "indexes" / book_id
    destination = base / version
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "pages.json").write_text(json.dumps(pages, ensure_ascii=False))
    (destination / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False))
    np.save(destination / "vectors.npy", vectors, allow_pickle=False)
    shutil.copyfile(pdf_path, destination / "source.pdf")
    usable = sum(page["status"] == "ok" for page in pages)
    manifest = {
        "version": version,
        "book_id": book_id,
        "model": MODEL_ID,
        "source_sha256": source_hash,
        "pipeline": PIPELINE_VERSION,
        "settings": asdict(settings),
        "pages": len(pages),
        "usable_pages": usable,
        "review_pages": [page["page"] for page in pages if page["status"] != "ok"],
        "chunks": len(chunks),
        "dimensions": int(vectors.shape[1]),
        "created_unix": int(time.time()),
        "manual_review_complete": False,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (base / "quality.json").write_text(
        json.dumps(
            {
                "pages": len(pages),
                "usable_pages": usable,
                "review_pages": manifest["review_pages"],
                "manual_review_complete": False,
            },
            indent=2,
        )
    )
    (base / "active.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def package_output(manifests: list[dict]):
    merged = {}
    for manifest in manifests:
        merged[manifest["book_id"]] = manifest
    for active_path in (OUTPUT_ROOT / "indexes").glob("*/active.json"):
        active = json.loads(active_path.read_text())
        merged[active["book_id"]] = active
    (OUTPUT_ROOT / "build-summary.json").write_text(
        json.dumps(
            {"indexes": [merged[key] for key in sorted(merged)]},
            indent=2,
        )
    )
    archive = Path("/kaggle/working/pathshala-indexes.zip")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in OUTPUT_ROOT.rglob("*"):
            if path.is_file():
                bundle.write(path, path.relative_to(OUTPUT_ROOT))
    print(f"\nREADY: {archive} ({archive.stat().st_size / 1024**2:.1f} MB)")
    print("Download it and extract its indexes/ directory into this repo's data/indexes/.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--book",
        choices=[*BOOKS, *BOOK_GROUPS, "all"],
        default="all",
        help="One book, the ssc/hsc group, or all four books",
    )
    parser.add_argument("--ocr-workers", type=int, default=2)
    parser.add_argument("--embed-batch-size", type=int, default=32)
    parser.add_argument("--dpi", type=int, default=250)
    parser.add_argument(
        "--ocr-engine",
        choices=["paddle-vl", "tesseract"],
        default="paddle-vl",
    )
    parser.add_argument(
        "--stage",
        choices=["all", "ocr", "index"],
        default="all",
        help="Use ocr and index separately when Paddle and PyTorch need isolated environments",
    )
    args = parser.parse_args()
    workers = 1 if args.ocr_engine == "paddle-vl" else max(1, min(args.ocr_workers, 4))
    settings = Settings(
        dpi=args.dpi,
        ocr_workers=workers,
        embed_batch_size=max(1, args.embed_batch_size),
    )
    tesseract_version = check_ocr() if args.stage != "index" else "not-used-during-index-stage"
    if args.book == "all":
        selected_ids = list(BOOKS)
    elif args.book in BOOK_GROUPS:
        selected_ids = BOOK_GROUPS[args.book]
    else:
        selected_ids = [args.book]
    selected = {book_id: BOOKS[book_id] for book_id in selected_ids}
    pdfs = locate_pdfs(selected_ids)
    if args.stage == "index":
        primary_ocr = type(
            "CachedPaddleOcr",
            (),
            {"name": f"paddleocr-vl-{PADDLE_OCR_VERSION}", "close": lambda self: None},
        )()
    else:
        primary_ocr = PaddleVLOcr() if args.ocr_engine == "paddle-vl" else TesseractOcr()
    print(
        f"Stage: {args.stage}; OCR primary: {primary_ocr.name}; "
        f"fallback: {tesseract_version}; embedding: {MODEL_ID}"
    )
    extracted = []
    for book_id in selected:
        source_hash, pages = extract_book(
            book_id,
            pdfs[book_id],
            settings,
            tesseract_version,
            primary_ocr,
            cache_only=args.stage == "index",
        )
        usable = sum(page["status"] == "ok" for page in pages)
        if usable < max(1, int(len(pages) * 0.5)):
            raise RuntimeError(f"{book_id}: only {usable}/{len(pages)} usable pages")
        extracted.append((book_id, source_hash, pages))

    primary_ocr.close()
    if args.stage == "ocr":
        total = sum(len(pages) for _, _, pages in extracted)
        print(f"OCR_READY: {total} page checkpoints under {WORK_ROOT / 'ocr'}")
        return

    import torch
    from sentence_transformers import SentenceTransformer

    if not torch.cuda.is_available():
        raise RuntimeError("Enable a Kaggle GPU accelerator before indexing")
    print(f"Embedding GPU: {torch.cuda.get_device_name(0)}")
    model = SentenceTransformer(MODEL_ID, device="cuda")
    model.max_seq_length = 512
    manifests = []
    for book_id, source_hash, pages in extracted:
        chunks = chunk_pages(book_id, source_hash, pages, model.tokenizer, settings)
        vectors = embed_chunks(model, chunks, settings)
        manifests.append(
            write_index(book_id, pdfs[book_id], source_hash, pages, chunks, vectors, settings)
        )
        print(json.dumps(manifests[-1], indent=2))
    package_output(manifests)


if __name__ == "__main__":
    main()
