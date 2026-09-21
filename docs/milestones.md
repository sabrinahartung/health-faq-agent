# Milestone plan

Nine milestones from toolchain to finished service. A box is ticked only when
the result is **in `main` and reproducible from a fresh clone** — not when it
works locally, and not when it sits on a branch.

Each completed milestone is published as a [release](https://github.com/sabrinahartung/health-faq-agent/releases),
so the repository's history shows what was finished when.

| # | Milestone | Status | Release |
|---|---|---|---|
| [M0](#m0-setup-and-toolchain) | Setup and toolchain | 🔨 almost done | — |
| [M1](#m1-corpus-and-retrieval-baseline) | Corpus and retrieval baseline | ✅ done | `v0.1.0` |
| [M2](#m2-agent-as-a-service) | Agent as a service | 🔨 in progress | — |
| [M3](#m3-container) | Container | ⬜ open | — |
| [M4](#m4-observability) | Observability | ⬜ open | — |
| [M5](#m5-evaluation-and-responsible-ai) | Evaluation and responsible AI | 🔨 groundwork in place | — |
| [M6](#m6-cicd) | CI/CD | 🔨 docs pipeline in place | — |
| [M7](#m7-kubernetes-optional) | Kubernetes | ⬜ optional | — |
| [M8](#m8-make-it-presentable) | Make it presentable | ⬜ open | — |

Legend: ✅ complete · 🔨 started · ⬜ not started

## M0 — Setup and toolchain

A reproducible environment: one Python version, one lockfile, one place where
configuration lives, and language models available locally so that no step of
the project ever needs an API key.

- [x] Python project managed with `uv`, version pinned, dependencies locked
- [x] Ollama running natively with `llama3.2:3b` and `bge-m3`
- [x] All configuration read from environment variables, nothing hard-coded
- [x] MIT licence
- [ ] `ruff` and `pytest` configured and running green

## M1 — Corpus and retrieval baseline

A retrieval agent is only as good as what it can retrieve. Before any agent
code, the project needed a corpus it is legally allowed to use, a chunking
strategy suited to statutory text, and a number saying how often the correct
provision actually reaches the context.

- [x] SGB V fetched reproducibly from `gesetze-im-internet.de`, licensing documented
- [x] 3,002 chunks indexed in ChromaDB, cut along subsections
- [x] Multilingual embeddings (`bge-m3`), chosen for a German corpus
- [x] Hand-written FAQ layer of 18 entries bridging everyday to legal phrasing
- [x] 33-question evaluation set, deliberately never indexed
- [x] Retrieval measured: **Recall@1 of 95 %**, against 68 % without the FAQ layer

## M2 — Agent as a service

Turning a set of scripts into something callable over HTTP that answers with
citations and decides for itself which tool to use — and where the refusal
boundary stops being an intention and becomes code.

- [ ] `GET /health` verifying Ollama, the model and the index
- [ ] `POST /ask` returning a validated response schema with citations
- [ ] Retrieval tool and a second tool, so the agent genuinely has a choice
- [ ] Citations validated against the retrieved context, not merely parsed
- [ ] Refusal path for individual medical questions
- [ ] Structured JSON logging throughout

## M3 — Container

Until the service runs in a container, "it works" means "it works on this
machine". One twist specific to this project: Ollama stays outside the
container, because inside one it loses GPU access on macOS.

- [ ] Multi-stage `Dockerfile`, non-root user, no build tools in the final image
- [ ] `docker compose` for the application and Chroma
- [ ] Healthcheck and startup ordering
- [ ] Configuration by environment variable, no secret in the image

## M4 — Observability

An agent that calls tools in a loop is opaque by default: when an answer is
wrong, you cannot tell whether retrieval missed, the model ignored the
context, or a tool failed silently. Tracing and metrics answer two different
questions and get two different tools.

- [ ] Langfuse tracing every tool call and every LLM call as its own span
- [ ] `/metrics` endpoint scraped by Prometheus
- [ ] Grafana dashboard: request rate, p95 latency, error rate, token use
- [ ] Dashboard provisioned from versioned JSON, not clicked together

## M5 — Evaluation and responsible AI

M1 measured whether the right text reaches the model. This measures whether
the model then does the right thing with it: does the answer follow from the
source, does the agent refuse when it must, and does it admit a gap when the
corpus is silent?

- [x] Evaluation set covering answerable, refusal and out-of-corpus questions
- [x] Retrieval harness reporting Recall@k and mean rank
- [ ] Groundedness and answer quality scored by an LLM judge
- [ ] Refusal rate measured, including false refusals
- [ ] Robustness: every question repeated with typos and as a paraphrase
- [ ] Evaluation runnable as a test suite, scores tracked over time

## M6 — CI/CD

So that the checks that matter run without anyone remembering to run them.

- [x] Documentation built and deployed to GitHub Pages on every push
- [ ] Lint, tests and container build on every push and pull request
- [ ] Evaluation suite as a separate, manually triggered workflow
- [ ] Failing checks block the merge

## M7 — Kubernetes (optional)

Scoped as optional on purpose, and the first thing to drop if anything
earlier runs long.

- [ ] Local `kind` cluster
- [ ] `Deployment`, `Service` and `ConfigMap` for the agent
- [ ] Deployed once, pod status and logs understood

## M8 — Make it presentable

Work that cannot be explained in five minutes is work nobody else can
evaluate.

- [ ] README with architecture diagram, evaluation results and screenshots
- [ ] Privacy and compliance: log redaction, no prompt persistence, local model
- [ ] Limitations stated plainly, including where the evaluation is optimistic

## Releases

Each milestone that reaches "done" is tagged and published as a GitHub
release, named for the milestone it completes:

| Tag | Milestone |
|---|---|
| `v0.1.0` | M1 — Corpus and retrieval baseline |
| `v0.2.0` | M2 — Agent as a service |
| `v0.3.0` | M3 — Container |

…and so on. A release is cut only when every box in the milestone is ticked,
which is what keeps the tag meaningful.
