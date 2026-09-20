# Logbook

Chronological, terse, wrong turns included. New entries go on top.

---

## 2026-09-20 — Documentation switched to English

Prose and code comments converted from German to English. The data files —
`faq.yaml` and `golden_set.yaml` — stay German, because they exist to match
German user queries; only their field names were anglicised. German terms of
art (*Familienversicherung*, *Belastungsgrenze*, *Zuzahlung*) are kept
untranslated.

The trigger was a word count: across 3,728 words of German documentation
there were already about 100 English technical terms — *retrieval*,
*embedding*, *chunking*, *recall*, *golden set*. The technical register was
English either way; the grammar around it was the only German part.

## 2026-09-20 — Documentation set up

MkDocs with the Material theme, deployed to GitHub Pages via Actions.
Decisions are recorded as numbered notes from now on, instead of being
reconstructed at the end.

## 2026-09-20 — FAQ layer and golden set

18 FAQ entries with 72 phrasings, 33 golden questions in three categories.
Measured effect: Recall@1 from 68 % to 95 %.

Key insight of the day: **an embedding model measures textual similarity, not
answer relevance.** Section 199a beat section 10 because its heading contains
the word "Studenten" — even though section 10 answers the question and 199a
does not.

Second insight: the FAQ layer and the golden set must never be the same file.
Details under [Evaluation](evaluation.md).

## 2026-09-20 — Bug: 71 provisions silently lost

The check `if "(weggefallen)" in body` discarded the **entire** provision as
soon as a single subsection had been repealed. Affected: 71 valid provisions,
among them section 39 (hospital treatment), section 31 (medicines),
section 35.

Noticed while reading a retrieval result, not by a test.
`where={"paragraph_nr": "39"}` returned an empty list.

Fix: filter per subsection rather than per provision. 2,501 → **3,002
chunks**. The script now logs discarded provisions and subsections
separately. At length in [Decision 003](decisions/003-chunking.md).

## 2026-09-20 — Corpus chosen and indexed

SGB V as XML from `gesetze-im-internet.de`, chunked by subsection, embedded
with `bge-m3`. First full index in 80 seconds.

First retrieval spot check: 2 of 5 everyday questions cleanly answered. Not
good enough — the trigger for the analysis that led to the FAQ layer.

## 2026-09-20 — Embedding model swapped

Replaced `nomic-embed-text` (from the plan) with `bge-m3`: the corpus is
German, the planned model is trained on English. Rationale under
[Decision 002](decisions/002-embedding-model.md).

## 2026-09-20 — Project structure flattened

`uv init health-faq-agent` had created a project directory **inside** the
already-initialised repository, and alongside it sat a PyCharm-created
`.venv` on Python 3.13 next to the 3.12 pinned by uv.

Since no commit existed yet, flattening was free: project files up one level,
both venvs discarded, `uv sync` afresh, `.gitignore` added.

!!! tip "Learned along the way"
    In PyCharm a venv-based interpreter is named `Python 3.12 (ProjectName)`.
    A bare `Python 3.12` without the parenthesised suffix points at a system
    or base interpreter — when in doubt check with
    `import sys; print(sys.executable)` in the Python console.
