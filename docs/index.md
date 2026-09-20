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

## Why this service exists

The project is a learning track along a real job profile: an agent service
that not only works, but is observable, evaluated and traceable. What is
documented here is therefore not only the result but the route — including
the wrong turns.

## Status

| Phase | Content | Status |
|---|---|---|
| 0 | Setup, toolchain, local models | ✅ done |
| 0 | Corpus chosen and indexed | ✅ done |
| 1 | FastAPI service, agent with tools | 🔨 in progress |
| 2 | Container, compose, podman | ⬜ open |
| 3 | Langfuse, Prometheus, Grafana | ⬜ open |
| 4 | Golden set, LLM-as-a-judge, refusal rate | 🔨 groundwork in place |
| 5 | CI/CD | 🔨 docs deployment in place |
| 6 | Kubernetes (optional) | ⬜ open |
| 7 | README, diagrams, walkthrough | ⬜ open |

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
