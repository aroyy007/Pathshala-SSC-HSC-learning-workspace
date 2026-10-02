# Contributing

## Before you start

Read [CONTEXT.md](../CONTEXT.md), [ARCHITECTURE.md](ARCHITECTURE.md), and the relevant ADR. The first release is four-book textbook QA; do not add board questions, guide solutions, or generated media to the textbook index without a source-class decision and rights record.

## Local setup

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
pnpm --dir apps/web install --frozen-lockfile
cp .env.example .env
```

Keep credentials in `.env`. Use synthetic evidence in tests; do not commit source text or API responses from private books.

## Development checks

Run the checks relevant to your change:

```bash
make test
make build
make audit
```

Retrieval changes must include a reproducible evaluation comparison. API changes must update [API.md](API.md) and the relevant tests. Corpus changes must update the source manifest and review record; never edit an active index manually.

## Branches and commits

Use a short branch name such as `feat/banglish-retrieval`, `fix/citation-validation`, or `docs/api-reference`. Keep commits focused and explain the user-visible or operational reason in the commit body when the change is non-obvious.

## Pull requests

Every pull request should state what changed and why, which commands were run and their result, whether API or schema behavior changed, whether private corpus data or secrets are involved, and what remains intentionally out of scope.

Do not claim tests or builds pass without fresh command output. Do not upload PDFs, OCR dumps, indexes, model caches, `.env` files, or provider credentials.
