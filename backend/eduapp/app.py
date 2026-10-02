import json, os, secrets, threading, time, uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from .config import ROOT, DATA, BOOKS, MODEL, GEMINI_MODEL, book_by_id
from . import store
from .retrieval import active, load_index, retrieve
from .generation import generate, ProviderError
from .banglish import expand_banglish, looks_banglish

@asynccontextmanager
async def lifespan(app):
 store.init();store.purge();yield

app=FastAPI(title='Pathshala API',version='0.1.0',lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['localhost','127.0.0.1','testserver'])
_locks=defaultdict(threading.Lock)
_rate=defaultdict(deque)
_rate_lock=threading.Lock()
_capacity=threading.BoundedSemaphore(2)

@app.middleware('http')
async def security(request,call_next):
 if request.method in ('POST','PUT','DELETE','PATCH'):
  origin=request.headers.get('origin')
  if origin and origin not in ('http://localhost:5173','http://127.0.0.1:5173','http://localhost:8000','http://127.0.0.1:8000'):
   return JSONResponse({'detail':'Origin not allowed'},status_code=403)
  try:
   if int(request.headers.get('content-length','0'))>16384: return JSONResponse({'detail':'Request too large'},status_code=413)
  except ValueError: return JSONResponse({'detail':'Invalid content length'},status_code=400)
 owner=request.cookies.get('pathshala_owner','')
 new=not (len(owner)==64 and all(c in '0123456789abcdef' for c in owner))
 if new: owner=secrets.token_hex(32)
 request.state.owner=owner
 res=await call_next(request)
 if new: res.set_cookie('pathshala_owner',owner,httponly=True,samesite='strict',secure=os.getenv('COOKIE_SECURE')=='1',max_age=86400)
 res.headers['X-Content-Type-Options']='nosniff'
 res.headers['Referrer-Policy']='same-origin'
 res.headers['X-Frame-Options']='SAMEORIGIN'
 if request.url.path.startswith('/api'): res.headers['Cache-Control']='no-store'
 return res

class SessionInput(BaseModel):
 collection_id: str
class MessageInput(BaseModel):
 text: str=Field(min_length=1,max_length=2000)
 answer_language: Literal['auto','bn','en']='auto'
 client_message_id: uuid.UUID
class SavedInput(BaseModel):
 enabled: bool
class FeedbackInput(BaseModel):
 rating: Literal['helpful','incorrect']

def owned(req,sid):
 s=store.session(req.state.owner,sid)
 if not s: raise HTTPException(404,'Conversation not found or expired')
 return s

def rate(owner):
 with _rate_lock:
  now=time.monotonic();q=_rate[owner]
  while q and q[0]<now-60: q.popleft()
  if len(q)>=10: raise HTTPException(429,'Please wait a moment before asking another question.',headers={'Retry-After':'60'})
  q.append(now)

@app.get('/health/live')
def live(): return {'status':'ok'}
@app.get('/health/ready')
def ready():
 available=[b['id'] for b in BOOKS if active(b['id'])]
 return JSONResponse({'status':'ready' if available else 'awaiting_books','ready_books':available},status_code=200 if available else 503)
@app.get('/api/v1/status')
def status():
 return {'generator':GEMINI_MODEL,'embedding':MODEL,'gemini_configured':bool(os.getenv('GEMINI_API_KEY')),'retrieval':'Dense + BM25 / RRF with Banglish expansion','storage':'Local SQLite + immutable NumPy vectors','retention_hours':24,'reranker_enabled':False,'banglish_enabled':True}
@app.get('/api/v1/corpora')
def corpora():
 result=[]
 for b in BOOKS:
  m=active(b['id']);q=DATA/'indexes'/b['id']/'quality.json'
  quality=json.loads(q.read_text()) if q.exists() else None
  result.append(b|{'status':'ready' if m and m['model']==MODEL else 'needs_index','pages':m['pages'] if m else None,'chunks':m['chunks'] if m else None,'version':m['version'] if m else None,'quality':quality,'pdf_available':(DATA/'raw'/f'{b["id"]}.pdf').exists()})
 return result
@app.get('/api/v1/sessions')
def sessions(req:Request): return store.sessions(req.state.owner)
@app.post('/api/v1/sessions',status_code=201)
def create_session(body:SessionInput,req:Request):
 if not book_by_id(body.collection_id): raise HTTPException(404,'Book not found')
 m=active(body.collection_id)
 if not m or m['model']!=MODEL: raise HTTPException(503,'This book is not indexed yet. Run the ingestion command first.')
 if len(store.sessions(req.state.owner))>=50: raise HTTPException(429,'Conversation limit reached. Delete an old conversation first.')
 return store.create(req.state.owner,body.collection_id,m['version'])
@app.get('/api/v1/sessions/{sid}/messages')
def messages(sid:str,req:Request):
 s=owned(req,sid)
 return {'session':{'id':s['id'],'book_id':s['book_id'],'version':s['version']},'messages':store.history(sid)}
@app.delete('/api/v1/sessions/{sid}',status_code=204)
def delete(sid:str,req:Request):
 owned(req,sid)
 lock=_locks[sid]
 if not lock.acquire(blocking=False): raise HTTPException(409,'Please wait for the current answer before deleting.')
 try: store.delete(req.state.owner,sid)
 finally: lock.release()
 return Response(status_code=204)
@app.post('/api/v1/sessions/{sid}/messages',status_code=201)
def answer(sid:str,body:MessageInput,req:Request):
 s=owned(req,sid);text=body.text.strip()
 if not text: raise HTTPException(422,'Enter a question')
 client=str(body.client_message_id)
 if not _locks[sid].acquire(blocking=False): raise HTTPException(409,'An answer is already being prepared in this conversation.')
 try:
  old=store.existing(sid,client)
  if old:
   if old['question']!=text or old['language']!=body.answer_language: raise HTTPException(409,'Message ID was already used for a different question')
   return old['result']
  rate(req.state.owner)
  if not _capacity.acquire(blocking=False): raise HTTPException(503,'The study assistant is busy. Please try again shortly.')
  try:
   start=time.monotonic();history=store.history(sid)
   query=text
   # Bounded context assist only for short anaphoric follow-ups; no extra LLM call.
   if history and len(text)<180 and any(w in text.casefold() for w in ('তিনি','তার ','এটা','সেটা','কেন','সে ','he ','she ','it ','why','that')):
    query=history[-1]['question']+'\nFollow-up: '+text
   variants=expand_banglish(query)
   evidence=retrieve(s['book_id'],s['version'],query,variants=variants)
   language=body.answer_language
   if language=='auto': language='bn' if any('\u0980'<=c<='\u09ff' for c in text) or looks_banglish(text) else 'en'
   result=generate(text,language,evidence,history)
   result.update({'id':str(uuid.uuid4()),'book_id':s['book_id'],'version':s['version'],'answer_language':language,'trace_id':str(uuid.uuid4()),'elapsed_ms':round((time.monotonic()-start)*1000)})
   store.add(sid,client,text,body.answer_language,result)
   return result
  except ProviderError as e: raise HTTPException(e.status,e.message)
  except (ValueError,FileNotFoundError): raise HTTPException(503,'This book index could not be loaded. Rebuild its index and try again.')
  finally: _capacity.release()
 finally: _locks[sid].release()
@app.get('/api/v1/sessions/{sid}/evidence/{eid}')
def evidence(sid:str,eid:str,req:Request):
 s=owned(req,sid)
 _,chunks,_,_=load_index(s['book_id'],s['version'])
 c=next((c for c in chunks if c['id']==eid),None)
 if not c: raise HTTPException(404,'Evidence not found in this book')
 return c|{'book_id':s['book_id'],'version':s['version'],'pdf_url':f'/api/v1/sessions/{sid}/pdf#page={c["page"]}'}
@app.get('/api/v1/sessions/{sid}/pdf')
def pdf(sid:str,req:Request):
 s=owned(req,sid)
 path=DATA/'indexes'/s['book_id']/s['version']/'source.pdf'
 if not path.exists(): raise HTTPException(404,'PDF not available')
 return FileResponse(path,media_type='application/pdf',headers={'Content-Disposition':'inline'})
@app.get('/api/v1/saved')
def saved(req:Request): return store.saved(req.state.owner)
@app.put('/api/v1/messages/{mid}/saved')
def save(mid:str,body:SavedInput,req:Request):
 if not store.message_owned(req.state.owner,mid): raise HTTPException(404,'Answer not found')
 store.save(req.state.owner,mid,body.enabled);return {'saved':body.enabled}
@app.put('/api/v1/messages/{mid}/feedback')
def feedback(mid:str,body:FeedbackInput,req:Request):
 if not store.message_owned(req.state.owner,mid): raise HTTPException(404,'Answer not found')
 store.feedback(req.state.owner,mid,body.rating);return {'recorded':True}

web=ROOT/'apps/web/dist'
if web.exists():
 app.mount('/assets',StaticFiles(directory=web/'assets'),name='assets')
 @app.get('/')
 def frontend(): return FileResponse(web/'index.html')
