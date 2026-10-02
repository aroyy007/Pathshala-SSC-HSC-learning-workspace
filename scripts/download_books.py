"""Download fixed publisher/mirror sources; never accepts arbitrary server-side URLs."""
import hashlib, json, urllib.request, urllib.parse, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
 'ssc-2026-bangla-1': ('1EL_DZGQXh-w2qVVlHKo_BWOXkiPWGF3R', 'https://nctbbooks.com/book/bangla-shahitto-class-nine-ten/'),
 'ssc-2026-bangla-2': ('14pcG6SDel6AUzrPZk2qzUjJb_9HYt-sg', 'https://nctbbooks.com/book/bangla-byakoron-class-nine-ten/'),
 'hsc-2026-bangla-1': ('11tNq5F0bfYFf5QexWOWAz3VlpryMlaFD', 'https://nctbbooks.com/book/bangla-shahittopath-class-eleven-twelve/'),
 'hsc-2026-bangla-2': ('https://www.ebookbou.edu.bd/Books/Text/OS/HSC/hsc_2851_2022.pdf', 'https://www.ebookbou.edu.bd/Books/Text/OS/HSC/hsc_2851_2022.pdf'),
}

def main():
 out = ROOT / 'data/raw'; out.mkdir(parents=True, exist_ok=True)
 for book, (source, landing) in SOURCES.items():
  path = out / f'{book}.pdf'
  if path.exists(): print(book, 'already downloaded', flush=True); continue
  url = source if source.startswith('https:') else f'https://drive.usercontent.google.com/download?id={source}&export=download&confirm=t'
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req, timeout=120) as res: data=res.read(100*1024*1024+1)
   if not data.startswith(b'%PDF-') or len(data)>100*1024*1024: raise ValueError('Response is not a PDF or exceeds size limit')
   path.write_bytes(data)
   path.with_suffix('.source.json').write_text(json.dumps({'source_url':landing,'download_url':url,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'edition_verified':False},indent=2))
   print(book, 'downloaded',len(data),'bytes',flush=True)
  except Exception as e: print(book,'failed:',type(e).__name__,str(e)[:120],flush=True)
if __name__=='__main__': main()
