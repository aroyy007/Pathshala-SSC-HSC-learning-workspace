---
status: accepted
---

# Explicit OCR review gate before activation

An index is not ready merely because OCR produced page checkpoints. Every flagged page must be reviewed, along with 20 randomly selected clean pages per book, chapter boundaries, and the pages supporting the supplied sample questions. Only a validated manifest with `manual_review_complete` set true may be activated for a release build.
