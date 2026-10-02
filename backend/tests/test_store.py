import sqlite3
import time
import pytest
from eduapp import store


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'DATA', tmp_path)
    store.init()


def conversation():
    session = store.create('alice', 'ssc-2026-bangla-1', 'version-one')
    result = {'id': 'answer-one', 'answer': 'শম্ভুনাথ', 'citations': []}
    store.add(session['id'], 'request-one', 'কাকে বলা হয়েছে?', 'bn', result)
    return session, result


def test_create_answer_retry_and_owner_isolation():
    session, result = conversation()
    assert store.session('alice', session['id'])['version'] == 'version-one'
    assert store.session('bob', session['id']) is None
    assert store.history(session['id'])[0]['result'] == result
    assert store.existing(session['id'], 'request-one')['result'] == result
    assert store.sessions('alice')[0]['title'] == 'কাকে বলা হয়েছে?'
    assert store.sessions('bob') == []
    assert store.message_owned('bob', result['id']) is None
    with pytest.raises(sqlite3.IntegrityError):
        store.add(session['id'], 'request-one', 'duplicate', 'bn', result)
    assert len(store.history(session['id'])) == 1


def test_delete_cascades_and_wrong_owner_cannot_delete():
    session, result = conversation()
    store.save('alice', result['id'], True)
    store.feedback('alice', result['id'], 'helpful')
    store.delete('bob', session['id'])
    assert len(store.saved('alice')) == 1
    store.delete('alice', session['id'])
    assert store.saved('alice') == []
    assert store.history(session['id']) == []
    with store.connection() as db:
        assert db.execute('SELECT COUNT(*) FROM feedback').fetchone()[0] == 0


def test_expiration_applies_to_saved_answers_and_mutations():
    session, result = conversation()
    store.save('alice', result['id'], True)
    with store.connection() as db:
        db.execute('UPDATE sessions SET created=? WHERE id=?', (time.time()-86401, session['id']))
    assert store.session('alice', session['id']) is None
    assert store.message_owned('alice', result['id']) is None
    assert store.saved('alice') == []
