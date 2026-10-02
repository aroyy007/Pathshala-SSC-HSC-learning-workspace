"""Evaluate retrieval against manually verified page labels; no LLM judge required.

JSONL fields: id, book_id, question, relevant_pages (one-based PDF pages).
Only answerable questions with verified labels belong in this retrieval set.
"""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from eduapp.config import book_by_id
from eduapp.retrieval import active, retrieve

parser=argparse.ArgumentParser()
parser.add_argument('dataset',type=Path)
parser.add_argument('--output',type=Path,default=Path('artifacts/retrieval-evaluation.json'))
args=parser.parse_args()
rows=[json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
if not rows:
    raise SystemExit('Dataset is empty; label evidence pages before evaluation')
results=[]
for row in rows:
    if not book_by_id(row['book_id']) or not row['relevant_pages'] or not all(type(p) is int and p>0 for p in row['relevant_pages']):
        raise SystemExit('Invalid collection or one-based evidence page labels')
    index=active(row['book_id'])
    if not index:
        raise SystemExit(f'No active index for {row["book_id"]}')
    start=time.perf_counter()
    hits=retrieve(row['book_id'],index['version'],row['question'],limit=5)
    pages=[hit['page'] for hit in hits]
    relevant=set(row['relevant_pages'])
    ranks=[rank for rank,page in enumerate(pages,1) if page in relevant]
    results.append({'id':row['id'],'book_id':row['book_id'],'version':index['version'],
        'retrieved_pages':pages,'page_recall_at_5':len(set(pages)&relevant)/len(relevant),
        'hit_at_5':int(bool(ranks)),'reciprocal_rank_at_5':1/min(ranks) if ranks else 0,
        'latency_ms':round((time.perf_counter()-start)*1000,2)})
report={'questions':len(results),'metrics':{key:statistics.mean(r[key] for r in results)
    for key in ('page_recall_at_5','hit_at_5','reciprocal_rank_at_5','latency_ms')},
    'notes':'Latency includes cold loading if applicable. Labels must be manually verified. No answer correctness claim.',
    'results':results}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report['metrics'],indent=2))
