"""Inspect PDF extraction and atomically activate a reproducible index."""
import hashlib,json,re,shutil,os
from pathlib import Path
import pymupdf as fitz
import numpy as np
from .config import DATA,MODEL,book_by_id
from .retrieval import embedder,encode,normalize

def extract(path,ocr=False):
 doc=fitz.open(path)
 if doc.is_encrypted or not 1<=len(doc)<=1000: raise ValueError('PDF is encrypted or exceeds page limit')
 pages=[]
 for i,page in enumerate(doc):
  text=normalize(page.get_text('text',sort=True))
  bengali=sum('\u0980'<=c<='\u09ff' for c in text)
  # Quarantine likely legacy-font/scan pages rather than treating gibberish as evidence.
  status='ok' if len(text)>60 and bengali>20 else 'review'
  method='native'
  raw_text=text
  if status=='review' and ocr:
   from .ocr import recognize
   text=normalize(recognize(path,i))
   bengali=sum('\u0980'<=c<='\u09ff' for c in text)
   status='ok' if len(text)>60 and bengali>20 else 'review'
   method='tesseract-ben-eng'
  pages.append({'page':i+1,'text':text,'raw_text':raw_text,'method':method,'status':status,'bengali_characters':bengali})
 doc.close()
 return pages

def chunk_pages(pages,tokenizer,book_id,source_hash):
 chunks=[]
 for page in pages:
  if page['status']!='ok': continue
  # Sentence-aware grouping; never crosses pages, keeping citation mapping exact.
  sentences=re.split(r'(?<=[।!?])\s+|\n\s*\n',page['text'])
  windows=[];buf=[];count=0
  for sentence in sentences:
   ids=tokenizer.encode(sentence,add_special_tokens=False)
   if len(ids)>420:
    if buf: windows.append(' '.join(buf));buf=[];count=0
    for start in range(0,len(ids),360): windows.append(tokenizer.decode(ids[start:start+420],skip_special_tokens=True))
   else:
    if count+len(ids)>350 and buf: windows.append(' '.join(buf));buf=[];count=0
    buf.append(sentence);count+=len(ids)
  if buf: windows.append(' '.join(buf))
  for j,text in enumerate(windows):
   if len(text.strip())<20: continue
   cid=hashlib.sha256(f'{source_hash}:{page["page"]}:{j}:{text}'.encode()).hexdigest()[:24]
   book=book_by_id(book_id)
   chunks.append({'id':cid,'page':page['page'],'text':text,'search_text':f'{book["level"]} Bangla Paper {book["paper"]} | {book["title"]}\n{text}'})
 return chunks

def ingest(book_id,path,ocr=False):
 if not book_by_id(book_id): raise ValueError('Unknown book')
 if path.stat().st_size>100*1024*1024: raise ValueError('PDF exceeds 100 MB')
 raw=path.read_bytes()
 if not raw.startswith(b'%PDF-'): raise ValueError('Not a PDF')
 sha=hashlib.sha256(raw).hexdigest()
 base=DATA/'indexes'/book_id
 base.mkdir(parents=True,exist_ok=True)
 pages=extract(path,ocr=ocr)
 content_hash=hashlib.sha256(json.dumps(pages,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 version=hashlib.sha256(f'{sha}:{content_hash}:{MODEL}:page-sentence-v2'.encode()).hexdigest()[:20]
 dest=base/version
 good=sum(p['status']=='ok' for p in pages)
 (base/'quality.json').write_text(json.dumps({'pages':len(pages),'usable_pages':good,'review_pages':[p['page'] for p in pages if p['status']!='ok']},indent=2))
 if good<max(1,len(pages)*0.5): raise ValueError(f'Extraction needs OCR review: only {good}/{len(pages)} usable Bengali pages. Index not activated.')
 tokenizer=embedder().tokenizer
 chunks=chunk_pages(pages,tokenizer,book_id,sha)
 if not chunks: raise ValueError('No usable chunks')
 print(book_id,'embedding',len(chunks),'chunks',flush=True)
 vectors=encode([c['search_text'] for c in chunks])
 if len(vectors)!=len(chunks) or not np.isfinite(vectors).all(): raise ValueError('Embedding validation failed')
 dest.mkdir(exist_ok=True)
 (dest/'chunks.json').write_text(json.dumps(chunks,ensure_ascii=False))
 (dest/'pages.json').write_text(json.dumps(pages,ensure_ascii=False))
 np.save(dest/'vectors.npy',vectors)
 shutil.copyfile(path,dest/'source.pdf')
 manifest={'version':version,'book_id':book_id,'model':MODEL,'source_sha256':sha,'pages':len(pages),'usable_pages':good,'chunks':len(chunks),'dimensions':vectors.shape[1]}
 (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
 temp=base/'active.tmp';temp.write_text(json.dumps(manifest));os.replace(temp,base/'active.json')
 return manifest
