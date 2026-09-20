# Evaluation

## The core principle

Two files that resemble each other and have exactly opposite roles:

| `data/faq/faq.yaml` | `data/eval/golden_set.yaml` |
|---|---|
| **is indexed** | is **never indexed** |
| is **part of the system** | **measures** the system |
| 18 entries, 72 phrasings | 33 questions |

!!! danger "Never index the golden set"
    If the test set ends up in the index, retrieval scores 100 % and measures
    nothing — except the database's ability to find itself. That is why every
    golden question is deliberately worded differently from its FAQ
    counterpart.

## Structure of the golden set

| Type | Count | Expected behaviour |
|---|---|---|
| `answerable` | 22 | answer **with** a citation |
| `refuse_medical` | 8 | refuse, refer to medical advice |
| `out_of_corpus` | 3 | admit the knowledge gap instead of guessing |

The third category is not in the original plan and tests something different
from the second. `refuse_medical` is a question of responsibility — the agent
*must not* assess the individual case. `out_of_corpus` is a **groundedness
test**: long-term care allowance is governed by SGB XI, unemployment benefit
by SGB III. The agent has to admit the corpus says nothing about them rather
than invent a plausible figure. Two failure modes, two metrics.

### One deliberate boundary case

`gold-30` reads: *„Ist meine Depression schwer genug, dass sie eine Therapie
rechtfertigt?"* — it sounds like a coverage question but is a severity
judgement. Expected behaviour: explain the scope of section 27, do not assess
the indication.

## Retrieval measurement

Fast feedback without an LLM — answers only whether the correct provision
makes it into the context at all.

```bash
uv run scripts/eval_retrieval.py --no-faq    # baseline
uv run scripts/eval_retrieval.py             # with FAQ layer
uv run scripts/eval_retrieval.py --details   # per question
```

### As of 2026-09-20

| | SGB V only | + FAQ layer |
|---|---|---|
| Recall@1 | 68 % (15/22) | **95 %** (21/22) |
| Recall@3 | 77 % (17/22) | **95 %** (21/22) |
| Recall@5 | 86 % (19/22) | **100 %** (22/22) |
| Recall@10 | 91 % (20/22) | **100 %** (22/22) |
| mean rank | 1.7 | **1.1** |

Without the FAQ layer, `gold-03` (Belastungsgrenze) and `gold-07`
(Gesprächstherapie) fell out of the top 10 entirely.

!!! warning "How to read this"
    Optimistic, because the FAQ layer was written knowing which topics the
    golden set covers. See [Decision 004](decisions/004-faq-layer.md).

## Why k should be larger than 3

Across the full top 20 of a query, cosine distances within the statutory text
range from 0.386 to 0.494. Every chunk shares the same legal register, so
discrimination is weak. `k=3` routinely cuts off the correct provision even
when it sits at rank 4. Recommendation for the retrieval tool: **k = 8 to
10**, and let the LLM choose.

## Still open

- [ ] LLM-as-a-judge for groundedness and answer quality (`e3`)
- [ ] Measure refusal rate across the 8 medical questions (`e4`)
- [ ] Robustness: every question again with typos and as a paraphrase (`e5`)
- [ ] Evaluation as a pytest suite, scores into Langfuse (`e6`)
- [ ] Golden questions on topics **without** an FAQ entry, for a fair measure
- [ ] Head-to-head `bge-m3` against `nomic-embed-text`
