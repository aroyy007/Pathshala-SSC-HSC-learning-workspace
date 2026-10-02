# Deployment

## Local development

The supported development topology is one FastAPI process and one Vite development process:

```bash
make dev-api
make dev-web
```

The API serves the built frontend when `apps/web/dist` exists. In development, Vite proxies API calls to port 8000.

## Build artifact

```bash
pnpm --dir apps/web install --frozen-lockfile
pnpm --dir apps/web build
```

The generated `apps/web/dist/` directory is ignored and can be served by the FastAPI process or a static host. Do not commit it unless a deployment platform explicitly requires checked-in artifacts.

## Environment

Copy `.env.example` to `.env` locally. Production values belong in the deployment secret manager:

| Variable | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes for live answers | Gemini generation credential |
| `HUGGINGFACE_API_KEY` | Optional | Private model download credential |
| `GEMINI_MODEL` | Yes/defaulted | Generator model identifier |
| `EMBEDDING_MODEL` | Yes/defaulted | Index-compatible embedding identifier |
| `EMBEDDING_DEVICE` | Optional | `cpu` or local accelerator selection |
| `EDUAPP_DATA_DIR` | Optional | Persistent private data root |
| `COOKIE_SECURE` | Yes in HTTPS deployment | Set to `1` for secure cookies |

The embedding model configured at runtime must match the active index manifest. A mismatch is a readiness failure, not a recoverable request error.

## Corpus deployment

Build indexes offline, review them, transfer the private ZIP through an approved channel, and run the importer on the target host. Do not build OCR or download large models in the API process. Keep the source and index directories on encrypted persistent storage with restricted permissions.

## Production caveats

The pilot is not yet a public SaaS deployment. Before exposing it to students, add authenticated users, HTTPS, durable database backups, distributed concurrency/rate limiting, structured redacted telemetry, cost budgets, a production vector store only after parity with the NumPy baseline, and rights approval for every source and generated media asset.

## Health checks

Use `/health/live` for process liveness and `/health/ready` for index/provider readiness. A `503` readiness response means the service should not receive student traffic for collections that are unavailable.
