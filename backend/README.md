# Backend

The backend is a FastAPI modular monolith. Run it from the repository root after installing the locked Python dependencies:

```bash
make dev-api
```

The package is loaded with `--app-dir backend`, so the import root is `backend/`. Application modules are documented in [Architecture](../docs/ARCHITECTURE.md), and endpoint contracts are in [API](../docs/API.md).

Run backend checks with:

```bash
make test
```

The backend expects private corpus artifacts under `data/` and reads provider credentials from the server environment only.
