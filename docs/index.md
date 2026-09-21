# Health FAQ Agent

A RAG agent that answers questions about **entitlements under German
statutory health insurance** — with a citation to the statute, running
entirely locally, without a single API key.

!!! info "Scope"
    The agent answers questions about **entitlements, benefits and
    co-payments**. It gives **no individual medical advice**. That boundary
    is not bolted on afterwards; it follows from the choice of corpus — see
    [Decision 001](decisions/001-corpus.md).

!!! note "Why the German vocabulary"
    The domain is German statutory health insurance. Terms such as
    *Familienversicherung*, *Belastungsgrenze* and *Zuzahlung* are terms of
    art with no clean English equivalent, and the corpus, the FAQ layer and
    the evaluation set are German by necessity — they have to match German
    user queries. Documentation and code are English; domain vocabulary is
    not translated.

## Why this project exists

A practice project for building a retrieval-augmented agent on a domain where
correctness matters and the limits of competence are sharp: entitlements under
German statutory health insurance.

The interesting part is not that it answers questions. It is what it takes to
know whether it answers them *well* — a corpus you are allowed to use, a
retrieval step you can measure, a refusal boundary you can defend, and traces
you can inspect when it goes wrong.

What is documented here is therefore not only the result but the route,
including the wrong turns.

## Roadmap

Nine milestones, from toolchain to walkthrough. The detail — what each one
means, what counts as done, and how to verify it — lives on one page that is
kept current with the code:

| # | Milestone | Status |
|---|---|---|
| M0 | Setup and toolchain | 🔨 almost done |
| M1 | Corpus and retrieval baseline | ✅ done |
| M2 | Agent as a service | 🔨 in progress |
| M3 | Container | ⬜ open |
| M4 | Observability | ⬜ open |
| M5 | Evaluation and responsible AI | 🔨 groundwork in place |
| M6 | CI/CD | 🔨 docs pipeline in place |
| M7 | Kubernetes | ⬜ optional |
| M8 | Make it presentable | ⬜ open |

→ **[Milestones](milestones.md)** for the checklists behind each line.

## Numbers today

<div class="grid cards" markdown>

-   **3,002**{ .lg } chunks

    ---

    SGB V statutory text, cut along subsections

-   **18**{ .lg } FAQ entries

    ---

    72 everyday phrasings bridging to legal language

-   **95 %**{ .lg } Recall@1

    ---

    against 68 % without the FAQ layer → [Evaluation](evaluation.md)

-   **€0**{ .lg } running cost

    ---

    Ollama, Chroma, Langfuse and Grafana all run locally

</div>

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

# check retrieval
uv run scripts/eval_retrieval.py
```

More under [Development](development.md).

## Disclaimer

The statutes used are **non-official** consolidated versions. Only the
*Bundesgesetzblatt* is authoritative. The agent therefore cites its source in
every answer rather than implying authority.
