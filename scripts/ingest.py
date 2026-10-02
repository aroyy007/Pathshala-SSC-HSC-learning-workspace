import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from eduapp.config import BOOKS,DATA
from eduapp.ingest import ingest
p=argparse.ArgumentParser();p.add_argument('--book',choices=[b['id'] for b in BOOKS]);p.add_argument('--ocr',action='store_true');args=p.parse_args()
failed=False
for b in BOOKS:
 if args.book and b['id']!=args.book: continue
 path=DATA/'raw'/f'{b["id"]}.pdf'
 if not path.exists(): print(b['id'],'missing PDF',flush=True);failed=True;continue
 try: print(ingest(b['id'],path,ocr=args.ocr),flush=True)
 except Exception as e: failed=True;print(b['id'],type(e).__name__,str(e)[:200],flush=True)
raise SystemExit(int(failed))
