# Health FAQ Agent

A retrieval-augmented agent that answers questions about **entitlements under
German statutory health insurance** — with a citation to the statute, running
entirely locally, without a single API key.

!!! info "Scope"
    The agent answers questions about **entitlements, benefits and
    co-payments**. It gives **no individual medical advice**. That boundary is
    not bolted on afterwards; it follows from the choice of corpus.

## Why this project exists

A domain where correctness matters and the limits of competence are sharp:
statutory entitlements are public, precisely worded and legally quotable,
while the neighbouring questions — *is my condition severe enough?* — must not
be answered by a language model at all.

The interesting problem is not producing an answer. It is knowing whether the
answer is any good: a corpus you are allowed to use, a retrieval step you can
measure, a refusal boundary you can defend, and traces you can inspect when it
goes wrong.

!!! note "Why the German vocabulary"
    The domain is German statutory health insurance. Terms such as
    *Familienversicherung*, *Belastungsgrenze* and *Zuzahlung* are terms of art
    with no clean English equivalent, so the corpus, the FAQ layer and the
    evaluation set are German by necessity. Documentation and code are English.

## Where it stands

| | |
|---|---|
| **3,002** | chunks of SGB V statutory text, cut along subsections |
| **18** | hand-written FAQ entries bridging everyday to legal language |
| **95 %** | Recall@1 on a 33-question evaluation set, against 68 % without the FAQ layer |
| **€0** | running cost — Ollama, Chroma, Langfuse and Grafana all run locally |

Current state: corpus and retrieval are built and measured; the agent service
is in progress. See the [milestone plan](milestones.md) for what is done and
what is not.

## How it works

Questions are embedded with `bge-m3`, matched against a Chroma index of SGB V
and a hand-written FAQ layer, and answered by `llama3.2:3b` running locally
through Ollama. Every answer carries the provision it rests on, or is an
explicit refusal. See [Architecture](architecture.md).

## Quick start

```bash
# provide the models
ollama pull llama3.2:3b
ollama pull bge-m3

# dependencies
uv sync

# load and index the corpus
uv run scripts/ingest_sgb5.py --rebuild
uv run scripts/ingest_faq.py

# check retrieval quality
uv run scripts/eval_retrieval.py
```

## Disclaimer

The statutes used are **non-official** consolidated versions from
`gesetze-im-internet.de`. Only the *Bundesgesetzblatt* is authoritative. The
agent therefore cites its source in every answer rather than implying
authority. Licensing and provenance are recorded in `SOURCES.md`.
