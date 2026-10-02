"""Resumable bounded OCR preparation; does not activate unreviewed indexes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import pymupdf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from eduapp.config import BOOKS, DATA
from eduapp.ocr import recognize

parser=argparse.ArgumentParser()
parser.add_argument('--book',choices=[b['id'] for b in BOOKS])
parser.add_argument('--sample',action='store_true',help='OCR five spread-out pages per book for manual review')
parser.add_argument('--workers',type=int,default=2,choices=range(1,5))
args=parser.parse_args()
jobs=[]
for book in BOOKS:
    if args.book and book['id'] != args.book:
        continue
    path=DATA/'raw'/f'{book["id"]}.pdf'
    with pymupdf.open(path) as pdf:
        count=len(pdf)
    pages=sorted({0,min(9,count-1),count//4,count//2,3*count//4}) if args.sample else range(count)
    jobs.extend((path,page) for page in pages)

def run(job):
    path,page=job
    text=recognize(path,page)
    return f'{path.stem} page {page+1}: {len(text)} characters'

with ThreadPoolExecutor(max_workers=args.workers) as pool:
    for result in pool.map(run,jobs):
        print(result,flush=True)
