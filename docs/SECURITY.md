# Security and privacy

## Security boundary

The current application is a local or controlled pilot. It uses an anonymous owner cookie rather than a full account system. Before public multi-device use, add authenticated identities, key rotation, abuse controls, secure cookie deployment, and a durable database strategy.

## Secrets

- `GEMINI_API_KEY` and `HUGGINGFACE_API_KEY` are backend-only.
- `.env` is ignored and must never be pasted into issues, notebooks, frontend code, or logs.
- Rotate any credential that has appeared in chat, terminal output, a screenshot, or a commit.
- Provider errors are mapped to safe messages; raw responses and credentials are not returned.

## Corpus privacy

Source PDFs, OCR text, embeddings, and indexes may be copyrighted or restricted. Keep them in private Kaggle datasets and ignored local directories until rights are documented. The GitHub repository contains pipeline code and metadata, not the source books.

## Application controls

- HTTP-only, SameSite owner cookie.
- Trusted-host middleware for the local host set.
- Same-origin checks on mutating requests.
- Request body and question-length limits.
- Per-owner request and session limits.
- Per-session concurrency lock and idempotent client message IDs.
- Collection/version scoping for retrieval, evidence, and PDF access.
- Exact citation-ID and quote validation before persistence.
- No arbitrary URL fetch or public PDF upload endpoint in the assessment release.

## Threats and mitigations

| Threat | Mitigation |
| --- | --- |
| Prompt injection inside OCR text | Treat question, history, and evidence as untrusted data; use a fixed system instruction and validate citations |
| Cross-session data access | Owner-scoped queries and session ownership checks |
| Cross-collection leakage | Session-pinned collection and corpus version |
| Provider credential exposure | Server-only environment variables and redacted errors |
| Resource exhaustion | Input limits, rate limits, bounded provider concurrency, page/size limits |
| Malicious index archive | Safe extraction, path checks, size limits, hash and vector validation |
| Wrong or stale evidence | Immutable version manifests and atomic activation |

## Pre-publication checklist

- Rotate development credentials.
- Run dependency and secret scans.
- Verify `.env`, `data/`, model caches, and artifacts are ignored.
- Confirm source rights for each PDF and derived artifact.
- Replace anonymous ownership with authenticated users if accounts are introduced.
- Configure HTTPS and `COOKIE_SECURE=1`.
- Add backups and restore tests before storing durable student data.
