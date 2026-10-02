# Evaluation

The application is not considered accurate because the model produces fluent Bengali. Evaluation separates retrieval, grounding, language compliance, abstention, and operational behavior.

## Dataset structure

The target textbook set contains 120 semantic case groups per collection, with Bengali and English variants. Groups are split together into development, validation, and sealed test partitions. Include direct facts, paraphrases, multi-passage questions, follow-ups, unsupported questions, ambiguity, false premises, and Banglish queries.

Each labeled case records:

- collection and corpus version;
- question language and text;
- prior turns when needed;
- answerable/unsupported status;
- expected behavior and answer aliases;
- source page numbers and reviewed source spans;
- annotator and second-review status.

The screenshot examples remain a smoke suite until a Bengali reviewer verifies their transcription and source pages.

## Metrics

| Area | Metric | Proposed gate |
| --- | --- | ---: |
| Retrieval | Passage Recall@5 | ≥ 0.90 |
| Retrieval | MRR@5 | Report per collection and language |
| Grounding | Supported factual claims | ≥ 0.95 |
| Answers | Correct answerable cases | ≥ 0.85 |
| Unknowns | Abstention recall on unsupported cases | ≥ 0.90 |
| Unknowns | Over-abstention on answerable cases | ≤ 0.10 |
| Citations | Resolving evidence IDs | 100% |
| Language | Requested answer language compliance | ≥ 0.95 |
| Isolation | Cross-collection leaks | 0 |
| Operations | Warm p95 answer latency | ≤ 10 seconds at 10 users |

Targets are release criteria, not current results. Report numerator, denominator, dataset hash, corpus hash, model revision, prompt revision, hardware, latency slices, and failures.

## Retrieval experiment

Run the same labels through dense-only Qwen retrieval, BM25-only retrieval, Qwen plus BM25 with RRF, and the selected hybrid configuration with an optional reranker. Keep chunking, query normalization, candidate limits, and labels constant across variants. Choose the simplest configuration that meets the quality gate and latency budget.

## Grounded answer review

Review a stratified sample for factual correctness, claim support, quote exactness, source-page correctness, requested-language compliance, appropriate abstention or clarification, and Banglish interpretation. No LLM judge is sufficient by itself for the release gate; Bengali academic review is required for the final test set.

## Running the current retrieval evaluator

Create a private JSONL file with one-based `relevant_pages` labels, then run:

```bash
.venv/bin/python scripts/evaluate.py \
  path/to/retrieval-labels.jsonl \
  --output artifacts/retrieval-evaluation.json
```

The current script reports page Recall@5, hit rate, reciprocal rank, and latency. It does not claim answer correctness or grounding; those require the reviewed answer set described above.
