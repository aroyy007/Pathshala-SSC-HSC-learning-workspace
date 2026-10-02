PYTHON ?= .venv/bin/python
PNPM ?= pnpm

.PHONY: dev-api dev-web test build ingest audit evaluate check
dev-api:
	$(PYTHON) -m uvicorn eduapp.app:app --app-dir backend --host 127.0.0.1 --port 8000
dev-web:
	$(PNPM) --dir apps/web dev
test:
	$(PYTHON) -m pytest -q
build:
	$(PNPM) --dir apps/web build
ingest:
	$(PYTHON) scripts/ingest.py
audit:
	$(PYTHON) scripts/audit_books.py
evaluate:
	$(PYTHON) scripts/evaluate.py $(DATASET)
check: test build
