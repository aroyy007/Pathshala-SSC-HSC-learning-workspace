import json
import zipfile

import numpy as np
import pytest

from scripts.import_kaggle_indexes import safe_extract, validate_book


def test_safe_extract_rejects_parent_path(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../outside.txt", "unsafe")
    with pytest.raises(ValueError, match="Unsafe path"):
        safe_extract(archive, tmp_path / "output")


def test_validate_book_checks_source_vectors_and_pages(tmp_path):
    book_id = "ssc-2026-bangla-1"
    version = "a" * 20
    base = tmp_path / "indexes" / book_id
    immutable = base / version
    immutable.mkdir(parents=True)
    pdf = b"%PDF- synthetic test bytes"
    (immutable / "source.pdf").write_bytes(pdf)
    source_hash = __import__("hashlib").sha256(pdf).hexdigest()
    pages = [{"page": 1, "text": "বাংলা পাঠ", "status": "ok"}]
    chunks = [{"id": "chunk-one", "book_id": book_id, "page": 1, "text": "বাংলা পাঠ"}]
    vectors = np.asarray([[0.6, 0.8]], dtype=np.float32)
    manifest = {
        "book_id": book_id,
        "version": version,
        "model": "Qwen/Qwen3-Embedding-0.6B",
        "source_sha256": source_hash,
        "pages": 1,
        "chunks": 1,
        "dimensions": 2,
        "manual_review_complete": False,
    }
    (immutable / "pages.json").write_text(json.dumps(pages))
    (immutable / "chunks.json").write_text(json.dumps(chunks))
    np.save(immutable / "vectors.npy", vectors)
    (immutable / "manifest.json").write_text(json.dumps(manifest))
    (base / "active.json").write_text(json.dumps(manifest))
    (base / "quality.json").write_text("{}")
    validated, validated_base = validate_book(tmp_path, book_id)
    assert validated == manifest
    assert validated_base == base

    vectors[0, 0] = np.nan
    np.save(immutable / "vectors.npy", vectors)
    with pytest.raises(ValueError, match="non-finite"):
        validate_book(tmp_path, book_id)
