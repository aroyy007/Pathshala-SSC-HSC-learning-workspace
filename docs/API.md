# API reference

The API is versioned under `/api/v1`. The current implementation returns resource objects directly rather than wrapping them in a `data` envelope. Errors use FastAPI's `detail` field. The public contract should remain stable even if the pilot storage moves from SQLite/NumPy to PostgreSQL/pgvector.

## Local server

```text
http://127.0.0.1:8000
```

Interactive OpenAPI is available at `/docs` during development.

## Authentication and ownership

The pilot uses an anonymous owner cookie named `pathshala_owner`. The server creates it on the first request as an HTTP-only, SameSite cookie. The cookie is the ownership boundary for sessions, messages, saved answers, feedback, evidence, and source PDFs. It is not an account system and should be replaced by an authenticated identity provider before public multi-device use.

Mutating requests accept same-origin development origins only. The default request body limit is 16 KiB. Question text is limited to 2,000 characters.

## Health and status

### `GET /health/live`

Returns process liveness: `{"status":"ok"}`.

### `GET /health/ready`

Returns `200` when at least one active collection is loadable and `503` while no collection is ready.

```json
{"status":"ready","ready_books":["ssc-2026-bangla-1"]}
```

### `GET /api/v1/status`

Returns configured model IDs and pilot capabilities. Credential values are never returned.

### `GET /api/v1/corpora`

Returns the four configured collections, their readiness, version, page/chunk counts, source note, and quality report when available.

## Sessions

### `GET /api/v1/sessions`

Lists up to 50 non-expired sessions owned by the current cookie.

### `POST /api/v1/sessions`

Creates a session pinned to a ready collection.

Request:

```json
{"collection_id":"ssc-2026-bangla-1"}
```

Response `201`:

```json
{"id":"session-uuid","book_id":"ssc-2026-bangla-1","version":"20-character-version"}
```

Possible errors: `404` unknown collection, `503` collection is not indexed, `429` owner has reached the session limit.

### `GET /api/v1/sessions/{session_id}/messages`

Returns the pinned session and its stored turns.

### `DELETE /api/v1/sessions/{session_id}`

Deletes the owned session and cascades its messages, saved-answer links, and feedback. Returns `204`.

## Questions

### `POST /api/v1/sessions/{session_id}/messages`

Creates or idempotently replays one answer.

Request:

```json
{
  "text":"অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
  "answer_language":"auto",
  "client_message_id":"uuid-generated-by-client"
}
```

`answer_language` is `auto`, `bn`, or `en`. Banglish input is detected by the server and expanded for retrieval; it is not stored as a separate corpus.

Response `201`:

```json
{
  "id":"answer-uuid",
  "book_id":"ssc-2026-bangla-1",
  "version":"20-character-version",
  "status":"answered",
  "answer":"...",
  "answer_language":"bn",
  "citations":[
    {"evidence_id":"chunk-id","page":42,"quote":"..."}
  ],
  "trace_id":"trace-uuid",
  "elapsed_ms":1234
}
```

Answer statuses are `answered`, `insufficient_evidence`, and `needs_clarification`. An `answered` result must contain at least one exact quote citation. A non-answered result contains no citations.

The same `client_message_id` returns the stored result when the question and requested language match. Reusing it with different content returns `409`.

## Evidence and source pages

### `GET /api/v1/sessions/{session_id}/evidence/{evidence_id}`

Returns the cited chunk, page, selected collection, corpus version, and a session-scoped PDF URL. Evidence IDs are accepted only from the session's pinned index.

### `GET /api/v1/sessions/{session_id}/pdf`

Streams the source PDF for the owned session with inline content disposition. It never exposes an arbitrary filesystem path.

## Saved answers and feedback

### `GET /api/v1/saved`

Lists saved answers owned by the current cookie.

### `PUT /api/v1/messages/{message_id}/saved`

Request: `{"enabled":true}`. Returns `{"saved":true}` or `{"saved":false}`.

### `PUT /api/v1/messages/{message_id}/feedback`

Request: `{"rating":"helpful"}`. `rating` is `helpful` or `incorrect`.

## Error behavior

| Status | Meaning |
| ---: | --- |
| 400 | Invalid request framing, such as malformed content length |
| 403 | Disallowed mutation origin |
| 404 | Unknown or non-owned resource |
| 409 | Duplicate ID conflict or concurrent session mutation |
| 413 | Request body exceeds the configured limit |
| 422 | Pydantic validation or empty question |
| 429 | Per-owner rate/session limit or upstream quota |
| 503 | Collection, provider, or local capacity unavailable |
| 504 | Provider deadline exceeded |

Clients should display the server's human-readable `detail` without exposing raw provider responses. Retry only `503` and `504` with bounded backoff; do not blindly retry `409`, `422`, or `429`.

## Compatibility rules

- Additive response fields are preferred within `v1`.
- Never change the meaning of a corpus version or evidence ID.
- A changed request contract requires a new API version or an explicit migration period.
- Trace IDs are diagnostic handles; they must never contain secrets or source text.
