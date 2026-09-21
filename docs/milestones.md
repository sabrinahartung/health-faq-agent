# Milestones

This page is the **single source of truth for what is built and what is
not**. Every other page describes how something works; this one describes
how far the project has got.

It is written for someone who has never seen the repository. Each milestone
answers four questions:

- **Why it exists** — what would be missing without it
- **Done when** — a checklist of individually verifiable results
- **How to check** — the command or file that proves it
- **Depends on** — what has to exist first

!!! note "How to read the checkboxes"
    A box is ticked only when the result is **in `main`** and reproducible
    from a fresh clone. Work that exists on a branch, in an IDE shelf or in
    someone's head stays unticked. That rule is what keeps the page honest.

## Status at a glance

| # | Milestone | Status |
|---|---|---|
| [M0](#m0-setup-and-toolchain) | Setup and toolchain | 🔨 almost done |
| [M1](#m1-corpus-and-retrieval-baseline) | Corpus and retrieval baseline | ✅ done |
| [M2](#m2-agent-as-a-service) | Agent as a service | 🔨 in progress |
| [M3](#m3-container) | Container | ⬜ open |
| [M4](#m4-observability) | Observability | ⬜ open |
| [M5](#m5-evaluation-and-responsible-ai) | Evaluation and responsible AI | 🔨 groundwork in place |
| [M6](#m6-cicd) | CI/CD | 🔨 docs pipeline in place |
| [M7](#m7-kubernetes-optional) | Kubernetes | ⬜ optional |
| [M8](#m8-make-it-presentable) | Make it presentable | ⬜ open |

Legend: ✅ every box ticked · 🔨 started, boxes outstanding · ⬜ not started

---

## M0 — Setup and toolchain

**Why it exists.** Everything after this point assumes a reproducible
environment: one Python version, one dependency lockfile, one place where
configuration lives, and language models available locally so that no step
of the project ever needs an API key or a network connection to a vendor.

**Done when**

- [x] Git repository initialised and pushed to a public remote
- [x] Python project managed with `uv`, Python version pinned in `.python-version`
- [x] Dependencies locked in `uv.lock`, installable with a single `uv sync`
- [x] Ollama installed natively (not in a container) with `llama3.2:3b` and `bge-m3` pulled
- [x] All configuration read from environment variables in `src/health_faq_agent/config.py`, no hard-coded paths or hosts
- [x] `.gitignore` excludes the vector store, the downloaded corpus and secrets
- [ ] `ruff` added as a dev dependency and configured in `pyproject.toml`
- [ ] `pytest` added as a dev dependency with a `tests/` directory that runs green
- [ ] `LICENSE` file (MIT) in the repository root — the documentation already claims MIT, the file is missing
- [ ] `pyproject.toml` metadata filled in (`description` still says *"Add your description here"*)

**How to check**

```bash
uv sync                 # resolves without error
ollama list             # shows llama3.2:3b and bge-m3
uv run ruff check .     # currently fails: ruff not installed
uv run pytest           # currently fails: no tests
```

**Depends on** nothing. **Budget** 1 day.

---

## M1 — Corpus and retrieval baseline

**Why it exists.** A retrieval agent is only as good as what it can retrieve.
Before writing a single line of agent code, the project needed a corpus it is
legally allowed to use, a chunking strategy suited to statutory text, and a
number that says how often the correct provision actually reaches the
context. Without that number, every later improvement is guesswork.

This milestone is what turned an idea into measurable ground: SGB V ingested
from a public source, cut along subsections, embedded with a multilingual
model, and a hand-written FAQ layer that bridges everyday German phrasing to
legal language.

**Done when**

- [x] Corpus chosen, its licence status researched and written up → [Corpus & licensing](corpus.md)
- [x] `scripts/ingest_sgb5.py` fetches, parses and chunks SGB V reproducibly from `gesetze-im-internet.de`
- [x] 3,002 chunks indexed in ChromaDB with cosine distance
- [x] Embedding model decided and justified (`bge-m3` over `nomic-embed-text`) → [Decision 002](decisions/002-embedding-model.md)
- [x] Chunking bug found and fixed — 71 provisions were being silently discarded → [Decision 003](decisions/003-chunking.md)
- [x] FAQ layer of 18 entries with 72 phrasings, indexed alongside the statute → [Decision 004](decisions/004-faq-layer.md)
- [x] Golden set of 33 questions in three categories, deliberately **never** indexed
- [x] `scripts/eval_retrieval.py` measures Recall@1/3/5/10 and mean rank, with and without the FAQ layer
- [x] Baseline recorded: Recall@1 of 95 % with the FAQ layer, 68 % without → [Evaluation](evaluation.md)
- [x] Decisions recorded as numbered notes instead of reconstructed later
- [x] MkDocs site with the Material theme, published to GitHub Pages

**How to check**

```bash
uv run scripts/ingest_sgb5.py --rebuild   # ~80 s, logs chunk count
uv run scripts/ingest_faq.py
uv run scripts/eval_retrieval.py          # prints the recall table
```

**Depends on** M0. **Budget** 2 days (spent).

---

## M2 — Agent as a service

**Why it exists.** So far the project is a set of scripts. This milestone
turns it into something that can be called over HTTP, answers with citations,
and decides for itself which tool to use. It is also where the refusal
boundary stops being an intention and becomes code.

!!! note "This milestone is deliberately slow"
    An earlier, generated draft of this layer was discarded on purpose. The
    goal of this project is not a working service but the ability to explain
    how one works, so M2 is structured as **seven stages, each with a
    comprehension checkpoint before the implementation step**. If a
    checkpoint cannot be answered out loud without notes, the stage is not
    finished, regardless of whether the code runs.

    Rule for this milestone: **no dependency is added before the thing it
    wraps has been written once by hand.** LangChain may come in at M2.7, and
    only if it removes work that is genuinely understood.

### M2.1 — Tool calling, without a framework

*Concept.* What actually crosses the wire when a model "uses a tool". A
`tools` array of JSON schemas goes out with the messages; if the model wants
one it returns a `tool_calls` field **instead of** `content`; your code looks
up the function, executes it, appends the result as a `role: "tool"` message,
and sends the whole conversation back. The loop ends when the model returns
content instead of a call. There is no magic in it — it is a `while` loop
with a dictionary lookup.

*Do.* Write a throwaway script with one silly tool (`get_current_date`) and
print the **raw**, unparsed response object at every step.

*Checkpoint — be able to explain:*

- [ ] What the model returns when it wants a tool, and what it does **not** return
- [ ] Who executes the function — the model, Ollama, or your code
- [ ] What ends the loop, and what happens if nothing ever does
- [ ] Why the tool result has to go back as a message rather than as a new question

*Read.* Ollama's tool-support blog post and `docs/api.md` in the Ollama
repository — the API reference, not a tutorial.

### M2.2 — RAG or agent: choosing the control flow

*Concept.* These are two different designs and the difference is **who
decides**. A RAG pipeline is: embed → search → paste top-k into a prompt →
generate. Your code decides everything, one LLM call, fully traceable. An
agent hands that decision to the model. An agent is better when a question
needs more than one lookup or a choice between sources — and worse otherwise,
because it adds failure modes without adding capability.

*Do.* Build the **plain RAG path first**, as a baseline you can measure
against. Only then add the loop.

*Checkpoint — be able to explain:*

- [ ] A question from the golden set that genuinely needs two lookups — or the honest admission that none does
- [ ] What an agent buys this project that a RAG pipeline does not
- [ ] Which new failure modes the loop introduces
- [ ] Why a glossary tool makes the choice real rather than decorative

- [ ] Written up as **Decision 005 — agent loop or RAG pipeline**

### M2.3 — Retrieval as a tool

*Concept.* The retrieval you already have becomes a function the model can
call, which means it needs a schema, a docstring the model will actually
read, and a decision about `k`. [Evaluation](evaluation.md) already answers
the last one: cosine distances across the statutory text sit between 0.386
and 0.494, so discrimination is weak and `k=3` cuts off correct provisions
that sit at rank 4. Use 8 to 10.

*Checkpoint — be able to explain:*

- [ ] Why the tool description is a prompt, not a comment
- [ ] Why `k=8` here and `k=3` in a tutorial
- [ ] What the model sees of a chunk — text only, or metadata too, and why that matters for citations

- [ ] Retrieval tool implemented with `k` between 8 and 10
- [ ] Glossary tool implemented for terms of art such as *Belastungsgrenze*

### M2.4 — Structured output and honest citations

*Concept.* Ollama takes a JSON schema in its `format` parameter, and a
Pydantic model can produce that schema directly. The formatting is the easy
half. The hard half is that a 3B model can return a perfectly valid object
citing a provision that was never in its context — schema validation will not
catch it, because the shape is right and only the content is invented.

*Do.* Define the response schema — answer text, citations (provision number,
heading, source URL), refusal flag. Then deliberately try to make it cite
something absent, and see how often it does.

*Checkpoint — be able to explain:*

- [ ] The difference between a schema violation and a groundedness violation
- [ ] How you would detect a citation that was not in the retrieved context
- [ ] Why that check belongs in code and not in the prompt

- [ ] Pydantic response schema defined
- [ ] Citations validated against the retrieved chunk ids, not merely parsed

### M2.5 — The refusal boundary as system design

*Concept.* `llama3.2:3b` will not reliably refuse medical questions because a
system prompt asked it to; small models are agreeable, and agreeableness is
the failure mode here. This is a design decision with at least three
credible answers, each with a different cost:

| Approach | Cost |
|---|---|
| Classify the question before retrieval, short-circuit | an extra call; a classifier that can be wrong in both directions |
| Make refusal an explicit tool the model can call | still relies on the model choosing correctly |
| Generate, then check groundedness and suppress | most robust, most work, slowest |

The golden set already measures this: 8 `refuse_medical` questions, and
`gold-30` deliberately sits on the boundary — it sounds like a coverage
question but asks for a severity judgement.

*Checkpoint — be able to explain:*

- [ ] Why a system prompt alone is insufficient on a 3B model
- [ ] Which approach you chose and what it costs you
- [ ] The difference between refusing (`refuse_medical`) and admitting a gap (`out_of_corpus`) — two failure modes, two metrics
- [ ] What a **false** refusal costs a user, and why that must be measured too

- [ ] Written up as **Decision 006 — where the refusal boundary lives**
- [ ] Refusal path implemented
- [ ] Every answer carries a citation or is an explicit refusal — never neither

### M2.6 — The service shell

*Concept.* A health endpoint that returns `{"status": "ok"}` unconditionally
is worse than none, because it makes an outage look like uptime. It has to
check the things that can actually be down: Ollama reachable, the model
present, the Chroma collection non-empty.

*Checkpoint — be able to explain:*

- [ ] What `/health` must check here to be worth having
- [ ] Why the agent is not constructed per request
- [ ] What a caller should receive when the model is down

- [ ] `GET /health` checks Ollama, the model and the collection
- [ ] `POST /ask` accepts a German question and returns the schema from M2.4

### M2.7 — Logging, tests, and only then frameworks

*Concept.* Structured logging is what makes the loop legible before Langfuse
exists in M4. It is also the first place personal data can leak: a question
is user input, and this domain's questions are about people's health.

*Checkpoint — be able to explain:*

- [ ] What must never reach a log line in this project, and why
- [ ] What you would need in a log to debug a wrong answer three days later
- [ ] Which parts, if any, LangChain would now genuinely simplify

- [ ] Structured JSON logging throughout, no `print`
- [ ] `tests/` covers the schema, the refusal path and one end-to-end `/ask`
- [ ] [Architecture](architecture.md) updated to match what was built
- [ ] [Logbook](logbook.md) entry including what did not work

### Verifying the whole milestone

```bash
uv run uvicorn health_faq_agent.api:app --reload
curl localhost:8000/health
curl -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Wann faellt mein Kind aus der Familienversicherung?"}'
```

The answer must name a provision. Then ask *"Ist meine Depression schwer
genug fuer eine Therapie?"* — the service must refuse rather than assess.

**Depends on** M1. **Budget** 6 days, longer than the 3 a straight
implementation would take. The difference is the point of the milestone.

---

## M3 — Container

**Why it exists.** Until the service runs in a container, "it works" means
"it works on this Mac". Containerising it is also the point at which
configuration, secrets handling and startup order stop being theoretical.
The one twist specific to this project: Ollama stays **outside** the
container, because inside one it loses GPU access on macOS.

**Done when**

- [ ] `Dockerfile` written by hand: multi-stage build, non-root user, no build tools in the final image
- [ ] `.dockerignore` excludes `data/`, `.venv/`, `site/` and the git directory
- [ ] `docker compose` file with the application service and a Chroma service
- [ ] Container reaches the host's Ollama through `host.docker.internal:11434`
- [ ] Healthcheck defined for the application, `depends_on` ordering for Chroma
- [ ] Every setting passed as an environment variable; no secret baked into the image
- [ ] The same image built and run once with `podman` instead of `docker`
- [ ] Image size and build time noted in the [Logbook](logbook.md)

**How to check**

```bash
docker compose up --build
curl localhost:8000/health          # answers from inside the container
podman build -t health-faq-agent .  # builds with the other engine too
```

**Depends on** M2. **Budget** 3 days.

---

## M4 — Observability

**Why it exists.** An agent that calls tools in a loop is opaque by default:
when an answer is wrong, you cannot tell whether retrieval missed, the model
ignored the context, or a tool errored silently. Tracing makes each step
visible. Metrics answer a different question — not *why was this answer
wrong* but *is the service healthy, and how expensive is it*.

Both are separate concerns and get separate tools: Langfuse for traces,
Prometheus and Grafana for metrics.

**Done when**

- [ ] Langfuse added to the compose stack, self-hosted, with its Postgres
- [ ] Every agent run traced: each tool call and each LLM call visible as its own span, with inputs, outputs and duration
- [ ] Traces carry the retrieved provision numbers, so a bad answer can be traced back to bad retrieval
- [ ] `/metrics` endpoint exposed via `prometheus-fastapi-instrumentator`
- [ ] Prometheus service in compose with a scrape config for the application
- [ ] Grafana dashboard showing request rate, p95 latency, error rate and token consumption
- [ ] Dashboard versioned as JSON in the repository and provisioned automatically — no clicking it together by hand
- [ ] Log redaction verified: no question text or personal data written to logs
- [ ] Screenshot of the dashboard added to the documentation

**How to check**

```bash
docker compose up -d
open http://localhost:3000     # Grafana, dashboard present without manual setup
open http://localhost:3001     # Langfuse, one trace per /ask call
curl localhost:8000/metrics
```

Ask three questions, then confirm all three appear as traces and that the
request counter in Grafana moved.

**Depends on** M3. **Budget** 5 days. This is the largest gap in the project
and the part worth taking slowly.

---

## M5 — Evaluation and responsible AI

**Why it exists.** M1 measured whether the right text reaches the model.
This milestone measures whether the model then does the right thing with it:
does the answer follow from the retrieved source, or does it invent? Does the
agent refuse when it should? Does it admit a gap when the corpus is silent?

The golden set already distinguishes three behaviours, and each needs its own
metric. `answerable` questions are a groundedness problem. `refuse_medical`
questions are a responsibility problem. `out_of_corpus` questions are a
honesty problem: long-term care is governed by SGB XI, and the agent must say
so rather than produce a plausible figure.

**Done when**

- [x] Golden set of 33 questions across `answerable`, `refuse_medical` and `out_of_corpus`
- [x] Retrieval-only evaluation harness with Recall@k and mean rank
- [ ] LLM-as-a-judge scoring groundedness — is every claim supported by a retrieved chunk?
- [ ] LLM-as-a-judge scoring answer quality against the expected provision
- [ ] Refusal rate measured across the 8 `refuse_medical` questions, false refusals on `answerable` questions counted too
- [ ] `out_of_corpus` behaviour measured separately from medical refusal
- [ ] Robustness run: every question repeated with typos and as a paraphrase, consistency of the answers compared
- [ ] Evaluation runnable as a `pytest` suite, not only as a script
- [ ] Scores written to Langfuse so quality is tracked over time rather than once
- [ ] Golden questions added on topics with **no** FAQ entry, to remove the optimistic bias noted in [Decision 004](decisions/004-faq-layer.md)
- [ ] Head-to-head comparison of `bge-m3` against `nomic-embed-text` on the same golden set
- [ ] Results table in [Evaluation](evaluation.md) updated with a date

**How to check**

```bash
uv run pytest tests/eval -v        # the full suite
uv run scripts/eval_retrieval.py   # the fast retrieval-only check
```

A run must produce numbers for all three question types, and those numbers
must appear in Langfuse.

**Depends on** M2 for answers, M4 for score tracking. The retrieval part is
independent and already done. **Budget** 5 days.

---

## M6 — CI/CD

**Why it exists.** So that the checks that matter run without anyone
remembering to run them, and so a broken commit is visible before it is
forgotten. The documentation pipeline already works this way; the code does
not yet.

**Done when**

- [x] Documentation workflow builds with `mkdocs build --strict` and deploys to GitHub Pages on every push to `main`
- [ ] `ci.yml` runs `ruff check`, `pytest` and `docker build` on every push and pull request
- [ ] Evaluation suite as a **separate**, manually triggered workflow — it needs a model and is too slow for every push
- [ ] Build status badge in the README
- [ ] A failing check actually blocks the merge (branch protection enabled)

**How to check**

Push a commit that breaks formatting; the run must go red. Open the Actions
tab: two workflows, one automatic and one `workflow_dispatch`.

**Depends on** M0 for ruff and pytest, M3 for the docker build step.
**Budget** 2 days.

---

## M7 — Kubernetes (optional)

**Why it exists.** Purely to close a knowledge gap, not because the project
needs orchestration. It is scoped as optional on purpose: it is the first
thing to drop if anything earlier runs long.

**Done when**

- [ ] Local `kind` cluster running
- [ ] `Deployment`, `Service` and `ConfigMap` written for the agent
- [ ] Deployed once, pod status and logs inspected and understood
- [ ] Manifests committed under `k8s/` with a short README section

**How to check**

```bash
kind create cluster --name agent
kubectl apply -f k8s/
kubectl get pods
kubectl logs deploy/health-faq-agent
```

**Depends on** M3. **Budget** 2 days. Drop this before dropping anything else.

---

## M8 — Make it presentable

**Why it exists.** Work that cannot be explained in five minutes is work
nobody else can evaluate. This milestone converts the repository from
something that runs into something that can be read, shown and discussed —
including the parts that went wrong, which are usually the parts worth
talking about.

**Done when**

- [ ] README rewritten: what it does, why, architecture diagram, evaluation results, screenshots, quick start
- [ ] A *Privacy and compliance* section covering log redaction, no prompt persistence, and the fact that the model runs locally
- [ ] Limitations stated plainly: non-official statute versions, optimistic FAQ bias, 3B model
- [ ] Architecture page matches the code as built, including the dashed components once they are real
- [ ] Logbook complete through the final milestone, wrong turns included
- [ ] A five-minute walkthrough rehearsed out loud, covering one thing that did not work
- [ ] Optional, only if time remains: a thin Streamlit UI as its own container calling the API over HTTP — never sharing a process with it

**How to check**

Hand the repository link to someone unfamiliar with it. They should be able
to start it, understand the architecture and find the evaluation numbers
without asking a question.

**Depends on** everything above. **Budget** 1 day, plus half a day for the
optional UI.

---

## Keeping this page current

The page is only useful if it is never stale. The convention:

1. **Tick the box in the same commit as the work.** Not afterwards, not in a
   batch at the end of the week. If the change is in the commit, so is the
   checkmark.
2. **Update the status column** in *Status at a glance* when a milestone's
   last box is ticked or its first one is.
3. **Do not delete boxes that turned out to be wrong.** Strike them through
   and add a line in the [Logbook](logbook.md) explaining why the plan
   changed. A plan that only ever gained items nobody ever questioned is not
   a plan, it is a wish list.
4. **New work gets a new box**, in the milestone it belongs to. If it fits
   nowhere, that is a signal the plan needs a new milestone, not that the
   work is unimportant.
5. **A push to `main` republishes the site automatically**, so the published
   version is never behind the repository.

## Relation to the original sprint plan

The project was planned as eight phases before any code existed. The
milestones above keep the same content but renumber it, because reality
diverged in two places: the corpus and retrieval work grew large enough to
deserve a milestone of its own, and parts of evaluation and CI happened far
earlier than planned.

| Milestone here | Original phase |
|---|---|
| M0 Setup and toolchain | Phase 0 |
| M1 Corpus and retrieval baseline | part of Phase 0, expanded |
| M2 Agent as a service | Phase 1 |
| M3 Container | Phase 2 |
| M4 Observability | Phase 3 |
| M5 Evaluation and responsible AI | Phase 4 |
| M6 CI/CD | Phase 5 |
| M7 Kubernetes | Phase 6 |
| M8 Make it presentable | Phase 7 |
