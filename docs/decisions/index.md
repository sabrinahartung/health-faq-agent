# Decisions

Short notes on the decisions that shaped the project, following the pattern
of *architecture decision records*. Each note records **what** was decided,
**why**, and **what argued against it**.

The point is not completeness but traceability: in three months it should be
possible to reconstruct why something looks the way it does. Superseded
decisions are not deleted but marked *superseded* and linked.

| No. | Title | Date | Status |
|---|---|---|---|
| [001](001-corpus.md) | SGB V as corpus | 2026-09-20 | accepted |
| [002](002-embedding-model.md) | bge-m3 instead of nomic-embed-text | 2026-09-20 | accepted |
| [003](003-chunking.md) | Chunking by subsection | 2026-09-20 | accepted |
| [004](004-faq-layer.md) | Hand-written FAQ layer | 2026-09-20 | accepted |

## Template

```markdown
# NNN — Title

**Date:** YYYY-MM-DD · **Status:** proposed | accepted | superseded

## Context
What situation forces a decision?

## Decision
What is being done?

## Rationale
Why this route?

## Alternatives rejected
What was considered, and why was it dropped?

## Consequences
What becomes easier, what becomes harder?
```
