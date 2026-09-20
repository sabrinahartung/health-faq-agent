# 001 — SGB V as corpus

**Date:** 2026-09-20 · **Status:** accepted

## Context

The plan called for "public health FAQs or benefit information" without
naming a source. Two requirements were in conflict:

1. The corpus should fit the domain of a health insurer.
2. The repository is public — so the content must be safely reusable.

That is exactly where the obvious sources fail: the FAQ pages of TK, AOK or
Barmer are topically perfect and copyrighted.

## Decision

The primary corpus is the **Sozialgesetzbuch Fünftes Buch (SGB V)**, obtained
as the XML full edition from `gesetze-im-internet.de`.

The corpus is **not** versioned in the repository. `scripts/ingest_sgb5.py`
fetches it reproducibly into `data/raw/`, excluded via `.gitignore`. The
script and the provenance note are what get versioned.

## Rationale

**Legally unambiguous.** Under section 5(1) UrhG, statutes carry no copyright
protection.

**Topically at the source.** The third chapter is literally titled
*"Leistungen der Krankenversicherung"* — the benefit information the plan
asked for, at the source rather than in a secondary account.

**Technically clean.** One 609 KB download, 809 structured `<norm>` elements
with section number and heading. No scraping, no `robots.txt` grey area, no
rate limiting.

**Citable by construction.** Every chunk carries a natural citation
(`§ 27 Abs. 1 SGB V`). The answer schema from phase 1 gets its source
references for free.

**It sharpens the scope.** "Health FAQ" is vague, and a vague scope makes the
refusal cases in the evaluation arbitrary. SGB V yields a defensible line:

> Questions about **entitlements, benefits and co-payments** are answered.
> Questions about the **individual medical case** are not.

## Alternatives rejected

| Source | Reason |
|---|---|
| TK, AOK, Barmer FAQs | copyrighted, not redistributable |
| gesund.bund.de | ministry content, no `robots.txt`, no usage licence published |
| IQWiG / gesundheitsinformation.de | high quality, but copyrighted |
| Wikipedia (CC BY-SA) | free, but holds no entitlement or benefit information |

## Consequences

**Easier:** licensing, citability, reproducibility, scope definition.

**Harder:** legal language sits far from everyday language. That has
measurable consequences for retrieval and led directly to
[Decision 004](004-faq-layer.md).

**Open flank:** statutory text is a chain of cross-references. Section 39(4)
does not state the co-payment amount; it refers to section 61 sentence 2. RAG
does not follow references. Some answers therefore need two chunks at once.
