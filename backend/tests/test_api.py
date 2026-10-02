import uuid
import pytest
from fastapi.testclient import TestClient
from eduapp import app as api, store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'DATA', tmp_path)
    monkeypatch.setattr(api, 'active', lambda book: {'version': 'v1', 'model': api.MODEL})
    monkeypatch.setattr(api, 'retrieve', lambda *args, **kwargs: [{'id': 'passage', 'page': 3, 'text': 'পনেরো বছর'}])
    monkeypatch.setattr(api, 'generate', lambda *args: {'status': 'answered', 'answer': 'পনেরো বছর', 'citations': [{'evidence_id': 'passage', 'page': 3, 'quote': 'পনেরো বছর'}]})
    monkeypatch.setattr(api, 'expand_banglish', lambda text: ['কল্যাণীর বয়স কত ছিল?'] if 'boyos' in text else [])
    api._rate.clear()
    with TestClient(api.app) as client:
        yield client


def test_chat_retry_save_feedback_and_delete(client):
    created = client.post('/api/v1/sessions', json={'collection_id': 'hsc-2026-bangla-1'})
    assert created.status_code == 201
    sid = created.json()['id']
    path = f'/api/v1/sessions/{sid}/messages'
    body = {'text': 'কল্যাণীর বয়স কত?', 'client_message_id': str(uuid.uuid4())}
    first = client.post(path, json=body)
    assert first.status_code == 201
    assert first.json()['answer_language'] == 'bn'
    assert client.post(path, json=body).json() == first.json()
    assert len(client.get(path).json()['messages']) == 1
    assert client.post(path, json=body | {'text': 'Different question'}).status_code == 409
    mid = first.json()['id']
    assert client.put(f'/api/v1/messages/{mid}/saved', json={'enabled': True}).status_code == 200
    assert len(client.get('/api/v1/saved').json()) == 1
    assert client.put(f'/api/v1/messages/{mid}/feedback', json={'rating': 'helpful'}).status_code == 200
    assert client.delete(f'/api/v1/sessions/{sid}').status_code == 204
    assert client.get(path).status_code == 404
    assert client.get('/api/v1/saved').json() == []


def test_other_browser_cannot_access_conversation(client):
    sid = client.post('/api/v1/sessions', json={'collection_id': 'ssc-2026-bangla-1'}).json()['id']
    with TestClient(api.app) as stranger:
        assert stranger.get(f'/api/v1/sessions/{sid}/messages').status_code == 404
        assert stranger.get(f'/api/v1/sessions/{sid}/pdf').status_code == 404
        assert stranger.delete(f'/api/v1/sessions/{sid}').status_code == 404


def test_invalid_input_and_origin(client):
    assert client.post('/api/v1/sessions', json={'collection_id': 'other'}).status_code == 404
    assert client.post('/api/v1/sessions', json={'collection_id': 'ssc-2026-bangla-1'}, headers={'Origin': 'https://untrusted.example'}).status_code == 403
    response = client.get('/health/live')
    assert response.status_code == 200
    assert response.headers['x-content-type-options'] == 'nosniff'


def test_banglish_uses_bengali_answer_language(client, monkeypatch):
    captured = {}
    monkeypatch.setattr(api, 'retrieve', lambda *args, **kwargs: captured.update(kwargs) or [{'id': 'passage', 'page': 3, 'text': 'পনেরো বছর'}])
    sid = client.post('/api/v1/sessions', json={'collection_id': 'hsc-2026-bangla-1'}).json()['id']
    response = client.post(
        f'/api/v1/sessions/{sid}/messages',
        json={'text': 'Kollyanir boyos koto chilo?', 'client_message_id': str(uuid.uuid4())},
    )
    assert response.status_code == 201
    assert response.json()['answer_language'] == 'bn'
    assert captured['variants'] == ['কল্যাণীর বয়স কত ছিল?']
