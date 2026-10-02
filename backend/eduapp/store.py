"""Local durable session store. All operations constrain resources by owner."""
import json, sqlite3, time, uuid
from contextlib import contextmanager
from .config import DATA

@contextmanager
def connection():
 conn=sqlite3.connect(DATA/'app.sqlite3',timeout=10)
 conn.row_factory=sqlite3.Row
 conn.execute('PRAGMA foreign_keys=ON')
 try:
  yield conn
  conn.commit()
 finally: conn.close()

def init():
 with connection() as db:
  db.executescript('''
  PRAGMA journal_mode=WAL;
  CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,owner TEXT NOT NULL,book_id TEXT NOT NULL,version TEXT NOT NULL,title TEXT NOT NULL,created REAL NOT NULL);
  CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,client_id TEXT NOT NULL,question TEXT NOT NULL,language TEXT NOT NULL,result TEXT NOT NULL,created REAL NOT NULL,UNIQUE(session_id,client_id));
  CREATE TABLE IF NOT EXISTS saved(owner TEXT NOT NULL,message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,PRIMARY KEY(owner,message_id));
  CREATE TABLE IF NOT EXISTS feedback(owner TEXT NOT NULL,message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,rating TEXT NOT NULL,PRIMARY KEY(owner,message_id));
  PRAGMA user_version=1;
  ''')

def purge():
 with connection() as db: db.execute('DELETE FROM sessions WHERE created<?',(time.time()-86400,))

def sessions(owner):
 purge()
 with connection() as db: return [dict(x) for x in db.execute('SELECT id,book_id,title,created FROM sessions WHERE owner=? ORDER BY created DESC LIMIT 50',(owner,))]

def create(owner,book_id,version):
 sid=str(uuid.uuid4())
 with connection() as db: db.execute('INSERT INTO sessions(id,owner,book_id,version,title,created) VALUES(?,?,?,?,?,?)',(sid,owner,book_id,version,'New conversation',time.time()))
 return {'id':sid,'book_id':book_id,'version':version}

def session(owner,sid):
 with connection() as db:
  row=db.execute('SELECT * FROM sessions WHERE id=? AND owner=? AND created>?',(sid,owner,time.time()-86400)).fetchone()
  return dict(row) if row else None

def history(sid):
 with connection() as db: return [dict(r) | {'result':json.loads(r['result'])} for r in db.execute('SELECT * FROM messages WHERE session_id=? ORDER BY created',(sid,))]

def existing(sid,client):
 with connection() as db:
  r=db.execute('SELECT * FROM messages WHERE session_id=? AND client_id=?',(sid,client)).fetchone()
  return dict(r) | {'result':json.loads(r['result'])} if r else None

def add(sid,client,question,language,result):
 with connection() as db:
  db.execute('INSERT INTO messages(id,session_id,client_id,question,language,result,created) VALUES(?,?,?,?,?,?,?)',(result['id'],sid,client,question,language,json.dumps(result,ensure_ascii=False),time.time()))
  db.execute("UPDATE sessions SET title=? WHERE id=? AND title='New conversation'",(question[:65],sid))

def delete(owner,sid):
 with connection() as db: db.execute('DELETE FROM sessions WHERE id=? AND owner=?',(sid,owner))

def message_owned(owner,mid):
 with connection() as db:
  r=db.execute('SELECT m.* FROM messages m JOIN sessions s ON m.session_id=s.id WHERE m.id=? AND s.owner=? AND s.created>?',(mid,owner,time.time()-86400)).fetchone()
  return dict(r) if r else None

def save(owner,mid,enabled):
 with connection() as db:
  if enabled: db.execute('INSERT OR IGNORE INTO saved VALUES(?,?)',(owner,mid))
  else: db.execute('DELETE FROM saved WHERE owner=? AND message_id=?',(owner,mid))

def saved(owner):
 purge()
 with connection() as db:
  return [dict(r)|{'result':json.loads(r['result'])} for r in db.execute('SELECT m.*,s.book_id FROM saved v JOIN messages m ON v.message_id=m.id JOIN sessions s ON m.session_id=s.id WHERE v.owner=? AND s.owner=? ORDER BY m.created DESC',(owner,owner))]

def feedback(owner,mid,rating):
 with connection() as db: db.execute('INSERT OR REPLACE INTO feedback VALUES(?,?,?)',(owner,mid,rating))
