# 002 — bge-m3 instead of nomic-embed-text

**Date:** 2026-09-20 · **Status:** accepted

## Context

The original plan named `nomic-embed-text`. That is the de-facto default in
the Ollama ecosystem: a BERT-style encoder (~137 M parameters) with rotary
embeddings and an 8192-token context, contrastively fine-tuned on roughly
235 million text pairs, Apache-2.0 including open training data.

The difference from a raw BERT is not the architecture but the training
objective: BERT was trained on masked language modelling, and its vectors are
poorly suited to similarity search. Only contrastive fine-tuning turns it
into a retrieval model.

**The problem:** `nomic-embed-text` v1.5 is trained on English. This
project's corpus is entirely German.

## Decision

`bge-m3` (BAAI, 567 M parameters, 1024 dimensions, 8k context) as the
embedding model — configurable via `EMBEDDING_MODEL`.

## Rationale

- Explicitly trained multilingually; German retrieval is not a by-product.
- 8k context, so even long provisions fit without splitting.
- Needs **no task prefixes**. `nomic-embed-text` expects `search_document:`
  and `search_query:`; Ollama does not add them automatically, and without
  them quality drops noticeably. A failure mode most tutorials miss.
- Available in Ollama, 1.2 GB, runs locally.

## Alternatives rejected

| Model | Reason |
|---|---|
| `nomic-embed-text` | English-centric, prefix trap |
| `nomic-embed-text-v2-moe` | multilingual, but less proven |
| `embeddinggemma` | smaller, but 768 dims and shorter context |
| `mxbai-embed-large` | strong in English, not multilingual |

## Consequences

`EMBEDDING_MODEL` is an environment variable from the start — switching
forces a full re-index, because both the dimensionality and the vector space
change.

**Still open:** a direct comparison of `bge-m3` against `nomic-embed-text` on
the golden set. The measuring tool already exists
(`scripts/eval_retrieval.py`); the comparison does not.
