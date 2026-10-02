"""Local OCR with atomic per-page checkpoints; original PDFs remain unchanged."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from functools import lru_cache
import pymupdf
from .config import DATA


@lru_cache(maxsize=8)
def source_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recognize(path, page_index, dpi=250):
    binary = shutil.which('tesseract')
    if not binary:
        raise ValueError('Install Tesseract with Bengali and English language data before OCR')
    version = subprocess.run([binary, '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    identity = f'{source_hash(str(path))}:{version}:ben+eng:{dpi}:psm3'
    cache = DATA / 'ocr' / hashlib.sha256(identity.encode()).hexdigest()[:24]
    cache.mkdir(parents=True, exist_ok=True)
    checkpoint = cache / f'{page_index+1:04d}.json'
    if checkpoint.exists():
        return json.loads(checkpoint.read_text())['text']
    with tempfile.TemporaryDirectory(prefix='page-', dir=cache) as scratch:
        image = Path(scratch) / 'page.png'
        with pymupdf.open(path) as pdf:
            pdf[page_index].get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB).save(image)
        result = subprocess.run(
            [binary, str(image), 'stdout', '-l', 'ben+eng', '--psm', '3'],
            capture_output=True, text=True, timeout=120,
            env=os.environ | {'OMP_THREAD_LIMIT': '1'},
        )
        if result.returncode:
            raise ValueError(f'OCR failed on PDF page {page_index+1}; check language data')
        temporary = Path(scratch) / 'result.json'
        temporary.write_text(json.dumps({'page': page_index+1, 'text': result.stdout, 'identity': identity}, ensure_ascii=False))
        os.replace(temporary, checkpoint)
    print(f'OCR page {page_index+1} cached', flush=True)
    return result.stdout
