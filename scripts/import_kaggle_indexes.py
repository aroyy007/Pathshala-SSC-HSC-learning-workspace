"""Validate and import the private Kaggle index bundle into data/indexes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BOOK_IDS = {
    "ssc-2026-bangla-1",
    "ssc-2026-bangla-2",
    "hsc-2026-bangla-1",
    "hsc-2026-bangla-2",
}
MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    total = 0
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            total += item.file_size
            if item.file_size > 150 * 1024 * 1024 or total > 1024 * 1024 * 1024:
                raise ValueError("Index archive exceeds import limits")
            path = Path(item.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe path in index archive")
            unix_mode = item.external_attr >> 16
            if stat.S_ISLNK(unix_mode):
                raise ValueError("Symbolic links are not allowed in index archives")
        bundle.extractall(destination)


def validate_book(root: Path, book_id: str) -> tuple[dict, Path]:
    base = root / "indexes" / book_id
    active = json.loads((base / "active.json").read_text())
    if active.get("book_id") != book_id or active.get("model") != MODEL_ID:
        raise ValueError(f"{book_id}: invalid book or model identity")
    version = active.get("version")
    if not isinstance(version, str) or not version.isalnum() or len(version) != 20:
        raise ValueError(f"{book_id}: invalid version")
    source = base / version / "source.pdf"
    chunks_path = base / version / "chunks.json"
    pages_path = base / version / "pages.json"
    vectors_path = base / version / "vectors.npy"
    manifest_path = base / version / "manifest.json"
    for required in (source, chunks_path, pages_path, vectors_path, manifest_path, base / "quality.json"):
        if not required.is_file():
            raise ValueError(f"{book_id}: missing {required.name}")
    with source.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise ValueError(f"{book_id}: invalid PDF")
    if sha256_file(source) != active.get("source_sha256"):
        raise ValueError(f"{book_id}: source checksum mismatch")
    manifest = json.loads(manifest_path.read_text())
    if manifest != active:
        raise ValueError(f"{book_id}: active and immutable manifests differ")
    pages = json.loads(pages_path.read_text())
    chunks = json.loads(chunks_path.read_text())
    vectors = np.load(vectors_path, allow_pickle=False)
    if len(pages) != manifest.get("pages") or len(chunks) != manifest.get("chunks"):
        raise ValueError(f"{book_id}: manifest counts differ")
    if vectors.ndim != 2 or vectors.shape != (len(chunks), manifest.get("dimensions")):
        raise ValueError(f"{book_id}: vector shape differs")
    if not np.isfinite(vectors).all():
        raise ValueError(f"{book_id}: vectors contain non-finite values")
    page_numbers = {page.get("page") for page in pages}
    if any(chunk.get("book_id") != book_id or chunk.get("page") not in page_numbers for chunk in chunks):
        raise ValueError(f"{book_id}: invalid chunk source mapping")
    if len({chunk.get("id") for chunk in chunks}) != len(chunks):
        raise ValueError(f"{book_id}: duplicate chunk IDs")
    return manifest, base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--activate-unreviewed",
        action="store_true",
        help="Allow activation while manual_review_complete is false",
    )
    args = parser.parse_args()
    if not args.archive.is_file() or not zipfile.is_zipfile(args.archive):
        raise SystemExit("Provide a valid pathshala-indexes.zip")
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pathshala-import-", dir=DATA) as scratch:
        staging = Path(scratch)
        safe_extract(args.archive, staging)
        found = {path.name for path in (staging / "indexes").iterdir() if path.is_dir()}
        if found != BOOK_IDS:
            raise ValueError(f"Expected exactly four book indexes; found {sorted(found)}")
        validated = [validate_book(staging, book_id) for book_id in sorted(BOOK_IDS)]
        if not args.activate_unreviewed and any(not manifest.get("manual_review_complete") for manifest, _ in validated):
            raise SystemExit(
                "Indexes validated but are marked unreviewed. Review OCR, then rerun with "
                "--activate-unreviewed for development or use the future reviewed-import workflow."
            )
        target_root = DATA / "indexes"
        target_root.mkdir(exist_ok=True)
        for manifest, source_base in validated:
            book_id = manifest["book_id"]
            destination = target_root / book_id
            if destination.exists():
                raise SystemExit(f"Refusing to overwrite existing index directory: {destination}")
            shutil.copytree(source_base, destination)
            print(f"Imported {book_id} version {manifest['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
