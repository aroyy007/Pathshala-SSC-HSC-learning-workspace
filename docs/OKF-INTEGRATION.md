# Open Knowledge Format (OKF) integration

## Decision

Pathshala may use the Open Knowledge Format (OKF) as a curated concept layer, but OKF does not replace the textbook PDF/OCR evidence index. The four source PDFs, page records, chunks, vectors, and review manifest remain the authority for factual citations.

OKF v0.2 is a portable directory of Markdown concept files with YAML frontmatter, normal Markdown links, and optional index/log files. It is useful for stable, human-reviewed knowledge that should be easy for students, agents, and GitHub readers to navigate.

## Good Pathshala concepts

- chapter and lesson summaries;
- grammar rules, exceptions, and worked examples;
- author, character, poem, and theme aliases;
- learning objectives and prerequisite concepts;
- reviewed easy explanations;
- links from a concept to exact textbook collection IDs and PDF pages;
- review status, source provenance, and stale-after dates.

## Do not auto-promote OCR

Raw OCR is a transcription artifact, not a trusted concept. A concept becomes eligible for the OKF bundle only after a Bengali reviewer verifies its wording, source page, collection, and academic scope. Generated explanations may be stored as `status: draft` or `status: unverified` until reviewed.

## Suggested bundle

```text
knowledge/
├── index.md
├── collections/
│   ├── ssc-2026-bangla-1.md
│   ├── ssc-2026-bangla-2.md
│   ├── hsc-2026-bangla-1.md
│   └── hsc-2026-bangla-2.md
├── concepts/
│   ├── grammar/
│   ├── literature/
│   └── writing/
└── log.md
```

Example concept shape:

```markdown
---
type: textbook-concept
title: অনুপমের সুপুরুষ
description: A reviewed concept for a character detail in the selected textbook.
status: human-reviewed
tags: [ssc, bangla-1, character]
generated:
  by: human-review
  at: 2026-10-03T00:00:00Z
sources:
  - collection_id: ssc-2026-bangla-1
    pdf_page: 42
    evidence_id: private-index-chunk-id
---

## Explanation

Keep the reviewed explanation here.

## Source

See the selected collection's evidence page in Pathshala.
```

The real private evidence ID and source wording must stay in the controlled corpus workflow until redistribution rights are verified. Do not commit copyrighted textbook passages to this public repository.

## Retrieval policy

Use OKF concepts before or alongside hybrid retrieval only for canonical, reviewed matches. For fuzzy questions across the books, use the existing collection-filtered dense/BM25/RRF pipeline. Preserve the OKF path, source class, review status, and corpus version in the trace so an answer can be inspected through both the curated concept and the original evidence.

## Why this is useful

OKF gives Pathshala a portable, Git-friendly layer for concepts that are expensive to rediscover from raw pages. It is especially suitable for SSC/HSC grammar rules and chapter navigation. It cannot solve OCR errors, source-rights questions, or missing evidence by itself, so it remains a reviewed supplement to the textbook index.
