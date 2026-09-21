# Health FAQ Agent

A retrieval-augmented agent that answers questions about **entitlements under
German statutory health insurance** — citing the statute it relies on, running
entirely locally, without a single API key.

📖 **[Documentation](https://sabrinahartung.github.io/health-faq-agent/)** ·
🗺️ **[Milestone plan](https://sabrinahartung.github.io/health-faq-agent/milestones/)**

> **Scope.** The agent answers questions about entitlements, benefits and
> co-payments. It gives **no individual medical advice** — a boundary that
> follows from the choice of corpus rather than being bolted on afterwards.

## Where it stands

| | |
|---|---|
| **3,002** | chunks of SGB V statutory text, cut along subsections |
| **18** | hand-written FAQ entries bridging everyday to legal language |
| **95 %** | Recall@1 on a 33-question evaluation set, against 68 % without the FAQ layer |
| **€0** | running cost — everything runs locally |

Corpus and retrieval are built and measured. The agent service is in progress;
observability and evaluation follow. The
[milestone plan](https://sabrinahartung.github.io/health-faq-agent/milestones/)
tracks what is done and what is not.

## How it works

Questions are embedded with `bge-m3` and matched against a Chroma index of SGB
V plus a hand-written FAQ layer that bridges everyday German phrasing to legal
language. `llama3.2:3b`, running locally through Ollama, answers from the
retrieved provisions. Every answer carries its source, or is an explicit
refusal.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com)
installed natively — inside a container Ollama has no GPU access on macOS.

```bash
git clone https://github.com/sabrinahartung/health-faq-agent.git
cd health-faq-agent

uv sync
ollama pull llama3.2:3b
ollama pull bge-m3

uv run scripts/ingest_sgb5.py --rebuild   # fetch, chunk and embed SGB V (~80 s)
uv run scripts/ingest_faq.py              # layer the FAQ on top
uv run scripts/eval_retrieval.py          # measure retrieval quality
```

Useful flags for the ingest script: `--dry-run`, `--limit N`, `--max-chars N`,
`--refresh`, `-v`.

## Configuration

Everything is read from environment variables, with defaults that work locally:

| Variable | Default |
|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` |
| `EMBEDDING_MODEL` | `bge-m3` |
| `CHAT_MODEL` | `llama3.2:3b` |
| `CHROMA_PATH` | `data/chroma` |
| `CHROMA_COLLECTION` | `sgb5` |

Changing `EMBEDDING_MODEL` requires a re-index — different models produce
different dimensions and live in different vector spaces.

## Data and licensing

The corpus is not versioned here; it is fetched reproducibly at runtime.
Statutes carry no copyright protection under section 5(1) UrhG. The versions
used are **non-official** consolidated texts from `gesetze-im-internet.de` —
only the *Bundesgesetzblatt* is authoritative, which is why the agent cites
its source rather than implying authority. Details in [SOURCES.md](SOURCES.md).

No patient data, no personal data, no individual medical advice.

## Licence

MIT — see [LICENSE](LICENSE).
