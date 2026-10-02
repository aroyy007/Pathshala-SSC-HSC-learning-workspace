# Pathshala context

Pathshala is a bilingual study assistant whose first release answers questions from four selected SSC/HSC Bangla textbooks. This glossary names the concepts that must stay consistent across the ingestion pipeline, API, interface, and evaluation documents.

## Curriculum and source language

**Collection**:
A student-selected textbook scope identified by exam level and paper, such as `ssc-2026-bangla-1`. A session belongs to one collection at a time.
_Avoid_: corpus, book category, subject filter

**Source class**:
The authority category of content, such as textbook, board question, licensed solution, or generated explanation. The first release admits textbook content only.
_Avoid_: content type, document kind

**Corpus version**:
An immutable, hashed edition of one collection's source PDF, extracted pages, chunks, and embeddings. A changed PDF or processing configuration creates a new corpus version.
_Avoid_: dataset version, index date

**Printed page**:
The page label printed in the source book. It can differ from the PDF page number and is retained separately when it can be identified.
_Avoid_: page number

## Retrieval and answers

**Evidence unit**:
A source-derived text chunk with a stable identifier and page mapping that can support an answer claim.
_Avoid_: context, snippet, passage result

**Grounded answer**:
An answer whose factual claims are supported by cited evidence units from the session's corpus version.
_Avoid_: AI answer, generated answer

**Abstention**:
A response that says the selected collection does not provide enough evidence to answer safely.
_Avoid_: fallback answer, empty answer

**Banglish query**:
Romanized Bengali typed with Latin characters, optionally mixed with English. It is a query-language input and is never treated as a separate source language.
_Avoid_: Roman Bangla, transliterated text

**Index readiness**:
The state reached only after all flagged OCR pages and the agreed representative sample have been reviewed, manifests validate, and the immutable index can be loaded.
_Avoid_: OCR complete, built index

## Product boundaries

**Assessment release**:
The first validated release: cited bilingual question answering over the four textbooks. Board questions, solutions, audio, and video are later source or learning modules.
_Avoid_: MVP platform, full Pathshala

**Private corpus**:
Source PDFs, OCR text, embeddings, and derived indexes restricted to local or explicitly authorized environments until usage rights are verified.
_Avoid_: internal dataset, hidden corpus
