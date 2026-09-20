# Development

## Prerequisites

- Python 3.12 (provided by uv via `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com), installed natively

!!! warning "Ollama natively, not in a container"
    Inside a container Ollama has no GPU access on macOS. Later, the container
    will point at `host.docker.internal:11434`.

## Setup

```bash
git clone https://github.com/sabrinahartung/health-faq-agent.git
cd health-faq-agent

uv sync

ollama pull llama3.2:3b
ollama pull bge-m3
```

## Building the corpus

```bash
# fetch SGB V, chunk, embed (~80 s)
uv run scripts/ingest_sgb5.py --rebuild

# layer the FAQ on top
uv run scripts/ingest_faq.py
```

Useful switches:

| Flag | Effect |
|---|---|
| `--dry-run` | parse and chunk only, embed nothing |
| `--limit 20` | only the first 20 chunks |
| `--max-chars 2000` | try a different chunk size |
| `--refresh` | re-download the XML instead of using the cache |
| `-v` | verbose logging |

## Measuring

```bash
uv run scripts/eval_retrieval.py --no-faq
uv run scripts/eval_retrieval.py
uv run scripts/eval_retrieval.py --details
```

## Documentation

```bash
# local, reloads on change
uv run mkdocs serve

# build statically
uv run mkdocs build --strict
```

!!! note "The local URL carries a path prefix"
    Because `site_url` ends in `/health-faq-agent/`, `mkdocs serve` serves
    under that path — `http://localhost:8000/` only redirects. The correct
    address is **http://localhost:8000/health-faq-agent/**.

A push to `main` builds and publishes the site to GitHub Pages automatically.

!!! note "One-time repository setting"
    **Settings → Pages → Build and deployment → Source: GitHub Actions.**
    Without it the workflow runs but nothing is published.

## Project layout

```
health-faq-agent/
├── data/
│   ├── eval/golden_set.yaml     # test set — NEVER index
│   ├── faq/faq.yaml             # FAQ layer — is indexed
│   ├── chroma/                  # vector store (gitignored)
│   └── raw/                     # downloaded XML (gitignored)
├── docs/                        # this documentation
├── scripts/
│   ├── ingest_sgb5.py
│   ├── ingest_faq.py
│   └── eval_retrieval.py
├── src/health_faq_agent/
│   └── config.py                # environment variables
├── mkdocs.yml
└── pyproject.toml
```

## Conventions

- **Language:** documentation and code in English; German kept for domain
  terms of art and for the data files, which have to match German queries.
- **Configuration only via environment variables**, never hard-coded.
- **Every decision worth the name** gets a note under `docs/decisions/`.
- **Wrong turns stay documented.** The ingest bug in
  [003](decisions/003-chunking.md) is part of the story, not a blemish on it.
