# RAG method and model decision

**Reviewed:** 11 September 2026. **Scope:** exactly four selected books, one for each SSC26/HSC26 Bangla paper. **Status:** researched design; no application or Bengali-book benchmark has run.

## Recommendation

Use **structure-aware contextual hybrid retrieval with bounded adaptive reranking**. This is an engineering composition of established techniques, not a claim to have implemented a particular named research system.

Start with `Qwen/Qwen3-Embedding-0.6B`, BM25, RRF, and `gemini-3.5-flash-lite`. Evaluate `BAAI/bge-m3` head-to-head before freezing embeddings. Add `BAAI/bge-reranker-v2-m3` only where its measured accuracy gain justifies query latency; compare `Qwen/Qwen3-Reranker-0.6B` if necessary. Use `gemini-3.5-flash` as a quality escalation candidate for grounded rule application and explanations, not to compensate for missing evidence.

There is no defensible “most efficient possible” claim before measuring these four PDFs on the deployment hardware. Efficiency means meeting the PRD's per-book quality requirements with the lowest cost per correct supported answer, subject to latency and memory limits. Model popularity and benchmark averages cannot establish the winner on Bengali textbook questions.

## What recent research changes

| Approach | Evidence reviewed | Decision for four books |
|---|---|---|
| Contextual retrieval | Anthropic describes enriching chunks before dense and BM25 indexing | Adopt source-derived book/chapter/section metadata first; evaluate generated chunk descriptions only for persistent context-loss errors |
| Late chunking | The original method pools chunk representations after long-context token encoding | Experimental alternative if context loss persists; requires compatible token-level embedding implementation |
| Modern chunking comparison, February 2026 | Reports task-dependent results and strong structure-based baselines | Keep paragraph/section chunking as the starting point; do not assume LLM segmentation is superior |
| RAGRouter-Bench, revised April 2026 | Studies quality/resource tradeoffs across query and corpus combinations | Measure routing decisions against a fixed baseline; no universal-method claim |
| AB-RAG, June 2026 preprint | Investigates confidence-guided retrieval under a finite budget | Adopt a bounded extra-pass policy as a design principle; do not transplant its confidence thresholds or claim reproduction |
| LightRAG | Graph and vector retrieval for relationships and broader discovery | Defer unless evaluated questions repeatedly need relationships missed by ordinary evidence retrieval |
| GraphRAG | Builds a graph, community hierarchy, and summaries | Defer for this fact/rule-focused scope; revisit only for corpus-wide thematic analysis |

These decisions are inferences for EDUApp. The paper abstracts and official method documentation were reviewed; experiments were not reproduced. Sources: [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval), [Late Chunking](https://arxiv.org/abs/2409.04701), [2026 chunking comparison](https://arxiv.org/abs/2602.16974), [RAGRouter-Bench](https://arxiv.org/abs/2602.00296), [AB-RAG](https://arxiv.org/abs/2606.29090), [LightRAG](https://arxiv.org/abs/2410.05779), [GraphRAG](https://microsoft.github.io/graphrag/).

## Concrete pipeline

### Ingestion: pay once

1. Extract and inspect Bengali text. OCR only pages with failed native extraction. Keep page mappings and original quotations.
2. Segment at book/work/section boundaries. Start with 350-token child chunks, cap at 500, and overlap at sentence boundaries up to 60 tokens. Grammar units keep rule, example, and exception together where possible.
3. Add a short deterministic index prefix: level, paper, verified book title, chapter, and heading. Use only metadata present in the source/manifest. Do not insert answer labels or synthetic facts.
4. Embed prefix plus chunk and build a BM25 index from the same representation. Store the unmodified canonical source separately for quotations and citations. Prefix tokens count toward the embedding limit.
5. Persist vector and lexical artifacts under the same book/index version. At this scale, begin with exact cosine search, not an approximate index chosen without a latency measurement.

This metadata prefix is a lightweight contextualization baseline, not equivalent to Anthropic's full LLM-generated contextual retrieval method. If generated descriptions are later tested, store them separately, audit factual additions, and never cite them as textbook evidence.

### Query: keep the normal path short

```text
Selected book + question
  -> resolve a follow-up only if needed
  -> dense top 20 and BM25 top 20 concurrently
  -> RRF merge, deduplicate, retain at most 20
  -> conditional reranking
  -> 3–5 original evidence units plus bounded parent context
  -> one answer-model call
  -> structural citation/quotation validation
  -> answer, clarification, or abstention
```

Use `RRF(d) = sum(1 / (60 + rank(d)))`, one-based ranks. Book scope is a hard filter in both retrievers, not a suggestion in the prompt. An English query can retrieve Bengali evidence through the multilingual encoder; BM25 alone is not the cross-language mechanism.

Initially compare reranking always-on versus always-off. Enable selective skipping only after a validation-set policy demonstrates that the skipped cases retain quality. Candidate routing signals include retriever agreement, calibrated score gaps, and explicit multi-part question structure. Agreement alone is not proof that the answer is supported. Do not interpret cosine or sigmoid scores as calibrated confidence.

On unclear evidence, permit at most one additional retrieval pass. On unresolved ambiguity, ask a clarification. Missing evidence never triggers an LLM switch to answer from memory. Use a shared request budget: maximum two retrieval passes and maximum three hosted LLM calls total, including any rewrite, generation, repair, or escalation; ordinary standalone questions target one. If the budget or deadline is exhausted, return the appropriate incomplete/error outcome.

For grammar application, generated examples must be labelled as generated and cite the underlying rule. Assess the application itself with Bengali reviewers; the presence of a cited rule does not prove the generated sentence is correct.

## Models to use

| Role | Starting model | Why this candidate | Important limit |
|---|---|---|---|
| Embedding | `Qwen/Qwen3-Embedding-0.6B` | Recent multilingual retrieval model with a relatively small model size | Not established as faster or better than BGE-M3 on these books |
| Embedding control | `BAAI/bge-m3` | Retain the original multilingual baseline | Use a separate model-specific index even though dimensions can match |
| Optional reranker | `BAAI/bge-reranker-v2-m3` | Multilingual cross-encoder already in the design | Added online computation; keep only if valuable |
| Reranker challenger | `Qwen/Qwen3-Reranker-0.6B` | Newer instruction-aware ranking candidate | Follow its scoring template; not a drop-in embedding call |
| Answer model | `gemini-3.5-flash-lite` | Current stable, latency/cost-oriented hosted candidate | Bengali correctness and account availability remain untested |
| Quality escalation | `gemini-3.5-flash` | Candidate for more demanding grounded explanations | Escalate only with adequate evidence and measured benefit |

Qwen's embedding card specifies 100+ languages, a 32K context, and up to 1024 output dimensions. Start at 1024. Use the documented query instruction and document encoding conventions; use its native pooling behavior. Do not bolt mean-pooled late chunking onto this model and assume equivalent semantics. A large context window is not an instruction to use enormous chunks. [Qwen embedding card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B).

Qwen's reranker has a distinct query/document scoring interface. Use official model-specific examples, rather than applying a generic classifier sigmoid to arbitrary logits. [Qwen reranker card](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B). BGE remains the comparator: [embedding](https://huggingface.co/BAAI/bge-m3), [reranker](https://huggingface.co/BAAI/bge-reranker-v2-m3).

Google lists `gemini-3.5-flash-lite` as stable with structured output support. This establishes available documented capability, not a Bengali performance result. Pin model IDs, prompt versions, and decoding settings in evaluation manifests. [Flash-Lite documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), [Flash documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash).

No fine-tuning, training dataset, graph database, autonomous agent framework, or separate model per textbook is required. Four books share the same models while retrieval remains isolated by book.

## Cost example and efficiency controls

At review time, Google's standard paid rates list Flash-Lite 3.5 at $0.30 per million input tokens and $2.50 per million output tokens, including thinking output. A hypothetical request with 3,000 input and 300 total billed output tokens costs **$0.00165**, or **$1.65 per 1,000 requests**, for that generation call alone. This is arithmetic, not measured application spend. It excludes retries, hidden/additional thinking beyond the assumed total, escalation, OCR, local compute, taxes, and hosting. [Provider pricing](https://ai.google.dev/gemini-api/docs/pricing).

Use short evidence bundles, batch offline embeddings, warm local models, cache normalized query embeddings by model revision, and avoid LLM rewriting for standalone questions. Do not repeatedly send an entire book because a model can accept it. Compare whole-book cached prompting as an experiment only if real traffic and token counts suggest it might be competitive; caching also has costs and retention constraints.

A newer generator is not necessarily the cheapest. Keep a lower-price available model as a cost-control experiment if its Bengali quality meets the same gates. Do not use long thinking for every simple fact question. Select supported generation settings through the provider adapter; do not assume all Gemini generations accept identical temperature/thinking controls.

## Smallest useful bake-off

Before constructing the full 960-query release set, create 20 reviewed semantic groups per book, paired Bengali/English: 160 queries total. Allocate half the groups to development and half to validation, keeping translations together. Include direct facts/rules, applications, context-dependent questions, and unsupported cases in each book. This pilot set supports early selection, not final release certification.

Run sequentially to avoid a costly full Cartesian product:

1. Compare Qwen and BGE embeddings under the same dense-only and hybrid retrieval settings.
2. Compare no prefix against source-derived prefix on the better candidates.
3. Compare reranking off/on and then the selective policy.
4. Hold retrieval fixed and compare Flash-Lite against Flash on correct gold context and retrieved context.
5. Measure warm p50/p95, memory, billed tokens, answer correctness, support, and abstention per book and language.

Select the cheapest configuration meeting all quality gates; require an observed benefit for every extra stage. Record confidence intervals and failures, not only averaged scores. If the pilot is inconclusive, keep the simpler baseline and expand annotation. Freeze the chosen configuration before evaluating the full sealed test set.

## What is complete and what is not

Complete: method comparison, candidate model selection, pipeline proposal, budget policy, and PRD updates. Not complete: PDF acquisition/validation, software implementation, hosted API testing, hardware profiling, or measured accuracy. The correct answer to “have you used the best RAG?” is therefore: **the design has been updated; no RAG system has been run yet, and a best-on-these-books claim would be premature.**
