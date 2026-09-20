# Architecture

## Overview

```mermaid
flowchart LR
    U[User] -->|question| API[FastAPI<br/>/ask]
    API --> AG[Agent]
    AG -->|tool 1| RET[Retrieval]
    AG -->|tool 2| GLO[Glossary lookup]
    RET --> CH[(ChromaDB<br/>3020 documents)]
    CH -->|context + citations| AG
    AG -->|prompt| LLM[Ollama<br/>llama3.2:3b]
    LLM --> AG
    AG -->|answer + citations| API
    API --> U

    RET -.embeddings.-> EMB[Ollama<br/>bge-m3]
    EMB -.-> CH

    AG -.traces.-> LF[Langfuse]
    API -.metrics.-> PR[Prometheus] --> GR[Grafana]

    style CH fill:#0f766e,color:#fff
    style LLM fill:#0f766e,color:#fff
    style EMB fill:#0f766e,color:#fff
    style LF stroke-dasharray: 5 5
    style PR stroke-dasharray: 5 5
    style GR stroke-dasharray: 5 5
```

Dashed: phase 3, not built yet.

## Ingest path

```mermaid
flowchart TD
    Z[xml.zip<br/>gesetze-im-internet.de] --> P[parse XML<br/>809 norm elements]
    P --> F{section norm<br/>with text?}
    F -->|no| X[discarded<br/>27 paragraphs]
    F -->|yes| A[split by subsection]
    A --> W{subsection<br/>repealed?}
    W -->|yes| Y[skipped<br/>99 subsections]
    W -->|no| L{> 3000<br/>characters?}
    L -->|yes| S[split at sentence bounds<br/>200 char overlap]
    L -->|no| C[chunk]
    S --> C
    C --> H[prepend heading]
    H --> E[bge-m3 embedding]
    E --> DB[(Chroma<br/>cosine)]

    FAQ[faq.yaml<br/>18 entries] --> E

    style DB fill:#0f766e,color:#fff
    style X fill:#7f1d1d,color:#fff
    style Y fill:#7f1d1d,color:#fff
```

## Why these components

| Component | Choice | Reason |
|---|---|---|
| Embedding | `bge-m3` | multilingual, German corpus → [002](decisions/002-embedding-model.md) |
| Generation | `llama3.2:3b` | runs natively on the Mac with GPU, 2 GB |
| Vector store | ChromaDB | embedded, no separate service needed |
| Distance | cosine | standard for sentence embeddings; Chroma defaults to L2 |
| Package manager | uv | fast, locks versions, manages the Python version |

## Configuration

All settings come from environment variables so nothing has to be touched
inside a container (`src/health_faq_agent/config.py`):

| Variable | Default |
|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` |
| `EMBEDDING_MODEL` | `bge-m3` |
| `CHAT_MODEL` | `llama3.2:3b` |
| `CHROMA_PATH` | `data/chroma` |
| `CHROMA_COLLECTION` | `sgb5` |
| `DATA_RAW_DIR` | `data/raw` |

!!! warning "Changing the model forces a re-index"
    Different embedding models produce different dimensions and live in
    different vector spaces. After changing `EMBEDDING_MODEL` you must run
    `ingest_sgb5.py --rebuild`.
