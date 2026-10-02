"""Immutable per-book exact dense search + BM25, fused with RRF."""
import json, os, threading, re, unicodedata
from functools import lru_cache
import numpy as np
from rank_bm25 import BM25Okapi
from .config import DATA, MODEL, ROOT
_model=None
_model_lock=threading.Lock()
_inference_lock=threading.Lock()

def normalize(text):
 return re.sub(r'[ \t]+',' ',unicodedata.normalize('NFC',text)).strip()

def tokens(text):
 # Python's \w excludes combining marks; preserve them explicitly.
 result=[]; word=''
 for c in normalize(text).casefold():
  if unicodedata.category(c)[0] in 'LMN': word+=c
  elif word: result.append(word);word=''
 if word: result.append(word)
 return result

def embedder():
 global _model
 with _model_lock:
  if _model is None:
   from sentence_transformers import SentenceTransformer
   import torch
   device=os.getenv('EMBEDDING_DEVICE','mps' if torch.backends.mps.is_available() else 'cpu')
   _model=SentenceTransformer(MODEL,token=os.getenv('HUGGINGFACE_API_KEY') or None,cache_folder=str(DATA/'models'),device=device)
   _model.max_seq_length=512
 return _model

def encode(texts,query=False):
 m=embedder()
 kwargs={}
 if query and 'Qwen3' in MODEL: kwargs['prompt']='Instruct: Retrieve Bengali textbook passages that answer the question.\nQuery: '
 if 'multilingual-e5' in MODEL: texts=[('query: ' if query else 'passage: ')+t for t in texts]
 with _inference_lock:
  return np.asarray(m.encode(texts,batch_size=8,normalize_embeddings=True,show_progress_bar=False,**kwargs),dtype=np.float32)

def active(book_id):
 p=DATA/'indexes'/book_id/'active.json'
 return json.loads(p.read_text()) if p.exists() else None

@lru_cache(maxsize=12)
def load_index(book_id,version):
 base=DATA/'indexes'/book_id/version
 meta=json.loads((base/'manifest.json').read_text())
 if meta['model']!=MODEL: raise ValueError('Index embedding model differs from configured model. Rebuild required.')
 chunks=json.loads((base/'chunks.json').read_text())
 vectors=np.load(base/'vectors.npy',allow_pickle=False)
 if len(chunks)!=len(vectors) or not np.isfinite(vectors).all(): raise ValueError('Invalid index')
 return meta,chunks,vectors,BM25Okapi([tokens(c['search_text']) for c in chunks])

def fuse(rankings):
 scores={}
 for ranking in rankings:
  for rank,idx in enumerate(ranking,1): scores[idx]=scores.get(idx,0)+1/(60+rank)
 return sorted(scores,key=lambda idx:(-scores[idx],idx))

def retrieve(book_id,version,question,limit=5,variants=None):
 meta,chunks,vectors,bm25=load_index(book_id,version)
 questions=list(dict.fromkeys([question]+list(variants or [])))[:3]
 query_vectors=encode(questions,query=True)
 if vectors.shape[1]!=query_vectors.shape[1]: raise ValueError('Embedding dimension mismatch')
 dense_scores=[vectors@q for q in query_vectors]
 lexical_scores=[bm25.get_scores(tokens(value)) for value in questions]
 rankings=[]
 for dense,lexical in zip(dense_scores,lexical_scores):
  rankings.append(np.argsort(-dense,kind='stable')[:20].tolist())
  rankings.append([int(i) for i in np.argsort(-lexical,kind='stable')[:20] if lexical[i]>0])
 selected=fuse(rankings)[:limit]
 return [dict(chunks[i],dense_score=float(max(score[i] for score in dense_scores)),lexical_score=float(max(score[i] for score in lexical_scores))) for i in selected]
