---
status: accepted
---

# SQLite and NumPy for the pilot

The assessment release uses SQLite for session metadata, immutable NumPy vector files for dense retrieval, and in-memory BM25 artifacts for the four-book pilot. This matches the current implementation and keeps corpus validation simple; a storage adapter remains the migration seam for PostgreSQL/pgvector when concurrency or corpus size justifies it.
