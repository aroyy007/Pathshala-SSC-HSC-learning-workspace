"""Measure source extraction without downloading or loading an embedding model."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from eduapp.config import BOOKS, DATA
from eduapp.ingest import extract


def main():
    output = DATA / 'audit'
    output.mkdir(parents=True, exist_ok=True)
    failed = False
    for book in BOOKS:
        path = DATA / 'raw' / f'{book["id"]}.pdf'
        try:
            pages = extract(path)
            report = {
                'book_id': book['id'],
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes': path.stat().st_size,
                'pages': len(pages),
                'usable_pages': sum(p['status'] == 'ok' for p in pages),
                'review_pages': [p['page'] for p in pages if p['status'] != 'ok'],
                'edition_verified': False,
                'quality_method': 'Initial length/Bengali-character heuristic; manual review still required',
            }
            (output / f'{book["id"]}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
            (output / f'{book["id"]}.pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2))
            print(json.dumps(report, ensure_ascii=False), flush=True)
        except Exception as exc:
            failed = True
            print(f'{book["id"]}: audit failed ({type(exc).__name__})', file=sys.stderr)
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
