from pathlib import Path

from kaggle import build_indexes


def test_locate_pdfs_only_requires_selected_books(tmp_path, monkeypatch):
    (tmp_path / "ssc-2026-bangla-1.pdf").write_bytes(b"%PDF-test")
    monkeypatch.setattr(build_indexes, "INPUT_ROOT", Path(tmp_path))

    located = build_indexes.locate_pdfs(["ssc-2026-bangla-1"])

    assert list(located) == ["ssc-2026-bangla-1"]
