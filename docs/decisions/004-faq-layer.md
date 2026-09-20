# 004 — Hand-written FAQ layer

**Date:** 2026-09-20 · **Status:** accepted

## Context

After the first complete index, retrieval gave mixed results on colloquial
questions. The most instructive failure:

> **Question:** „Bin ich als **Studentin** bei meinen **Eltern
> mitversichert**?"
> *(Am I, as a student, covered through my parents?)*

| Hit | Why |
|---|---|
| **rank 1** — § 199a *Informationspflichten bei krankenversicherten **Studenten*** | shares a word |
| **rank 4** — § 10 *Familienversicherung* | shares **no** word |

Section 10 is the correct answer. It never says *Studentin*, never
*mitversichert*, never *Eltern* — it says *Kinder von Mitgliedern*.

## The diagnosis

An embedding model does not measure "does this text answer this question" but
"do these two texts resemble each other". Those are not the same thing.
A question and its answer are written in different registers, by different
people, for different purposes. The literature calls this
**query–document asymmetry**.

Two properties of the corpus compound it:

- **Statutory text is a chain.** Section 39(4) does not state the amount; it
  refers to section 61 sentence 2. RAG fetches chunks, it does not follow
  references.
- **The statute states entitlements, not cases.** „Meine Tochter ist 20 und
  arbeitet nicht" requires *applying* section 10(2) no. 2.

Also striking was the **narrow distance band**: across the entire top 20,
cosine distances lay between 0.386 and 0.494. Every chunk shares the same
legal register, so discrimination is correspondingly weak.

## Decision

A second, hand-written layer in `data/faq/faq.yaml`: 18 entries with 72
phrasings in total. Each entry bundles an everyday question, several
paraphrases, a short answer in plain German and the source reference.

All phrasings of an entry land in **one** document. The vector then sits in
the middle of the paraphrases and covers a wider range without flooding the
result list with duplicates of the same entry.

The layer lives in the **same** collection as the statutory text, marked with
`type: faq`. A query hits both; the metadata field allows the layer to be
hidden for comparison runs.

## Effect

22 answerable questions from the golden set:

| | SGB V only | + FAQ layer |
|---|---|---|
| Recall@1 | 68 % | **95 %** |
| Recall@3 | 77 % | **95 %** |
| Recall@5 | 86 % | **100 %** |
| mean rank | 1.7 | **1.1** |

!!! warning "This number is optimistic"
    The FAQ entries were written knowing the topics of the golden set. The
    *wording* deliberately differs, the *topics* overlap. A fair measure needs
    golden questions on topics the FAQ layer does not cover. The 100 % is a
    waypoint, not a seal of quality.

## Alternatives rejected

| Approach | Reason |
|---|---|
| Each paraphrase as its own chunk | floods the result list with duplicates |
| Reranker (`bge-reranker-v2-m3`) | effective, but more expensive — measure first, then build |
| Hybrid search (BM25 + dense) | likewise; sensible once the FAQ layer is exhausted |
| A larger LLM instead of better retrieval | does not address the cause |

## Consequences

The FAQ layer is **part of the system**, not of the evaluation. Its
counterpart, `data/eval/golden_set.yaml`, is **never** indexed — see
[Evaluation](../evaluation.md).
