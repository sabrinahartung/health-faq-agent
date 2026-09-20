# 003 — Chunking by subsection

**Date:** 2026-09-20 · **Status:** accepted

## Context

The provisions of SGB V vary wildly in length: the median is around 1,900
characters, the 90th percentile 8,000, and the longest (section 87) exceeds
55,000. One chunk per provision would be unusable; a fixed character window
cuts through units of meaning.

## Decision

Three stages:

1. **Split by subsection.** Markers `(1)`, `(2)`, `(2a)` at the start of a
   line each begin a chunk.
2. **Split over-long subsections at sentence boundaries**, default 3,000
   characters with 200 characters of overlap.
3. **Prepend the heading.** Every chunk starts with
   `§ 27 Krankenbehandlung (SGB V), Absatz 1`.

Result: **3,002 chunks**, median 656 characters.

## Rationale

The subsection is the natural unit of meaning in statutory text — and at the
same time the conventional unit of citation. One chunk therefore corresponds
to exactly one source reference (`§ 39 Abs. 4 SGB V`), which serves the
answer schema from phase 1 directly.

The prepended heading is not decoration. Without it `bge-m3` sees only bare
statutory prose; the topical anchor — what this provision is actually about —
is missing from the vector.

## Pitfalls in the source XML

**Lists run together.** Marker and text sit in separate `<DT>`/`<DD>`
elements. A naive `itertext()` produces
`umfaßt 1.Ärztliche Behandlung 2.zahnärztliche` — so the renderer walks the
pairs and re-inserts breaks.

**`(weggefallen)` — an expensive mistake.** Repealed subsections carry the
text `(weggefallen)`. The first version of the script checked for this at the
level of the *provision*:

```python
if not body or "(weggefallen)" in body:
    continue          # discards the ENTIRE provision
```

That silently removed **71 valid provisions**, among them section 39
(hospital treatment), section 31 (medicines) and section 35 (reference
prices) — each of which contains a single repealed subsection somewhere.

It surfaced only because a test question about hospital co-payments returned
the wrong provision, and the follow-up query
`where={"paragraph_nr": "39"}` came back empty. The fix filters per
subsection:

```python
kern = ABSATZ_RE.sub("", abs_text).strip()
if not kern or kern == "(weggefallen)":
    dropped_absaetze += 1
    continue          # skip only THIS subsection
```

**501 chunks more**, and section 39(4) now lands at rank 2 for the hospital
question instead of not being in the index at all.

!!! note "Lesson"
    Silent data loss in the ingest looks exactly like poor retrieval. The
    script therefore now logs how many provisions and how many subsections it
    discards — a number that makes you pause while reading is worth more than
    a quiet `continue`.

## Consequences

Chunk size, overlap and batch size are CLI parameters (`--max-chars`,
`--overlap`, `--batch-size`) and can be swept against `eval_retrieval.py`
without touching the code.
