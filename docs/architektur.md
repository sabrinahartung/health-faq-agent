# Architektur

## Überblick

```mermaid
flowchart LR
    U[Nutzerin] -->|Frage| API[FastAPI<br/>/ask]
    API --> AG[Agent]
    AG -->|Tool 1| RET[Retrieval]
    AG -->|Tool 2| GLO[Glossar-Lookup]
    RET --> CH[(ChromaDB<br/>3020 Dokumente)]
    CH -->|Kontext + Zitate| AG
    AG -->|Prompt| LLM[Ollama<br/>llama3.2:3b]
    LLM --> AG
    AG -->|Antwort + Fundstellen| API
    API --> U

    RET -.Embeddings.-> EMB[Ollama<br/>bge-m3]
    EMB -.-> CH

    AG -.Traces.-> LF[Langfuse]
    API -.Metriken.-> PR[Prometheus] --> GR[Grafana]

    style CH fill:#0f766e,color:#fff
    style LLM fill:#0f766e,color:#fff
    style EMB fill:#0f766e,color:#fff
    style LF stroke-dasharray: 5 5
    style PR stroke-dasharray: 5 5
    style GR stroke-dasharray: 5 5
```

Gestrichelt: Phase 3, noch nicht gebaut.

## Ingest-Pfad

```mermaid
flowchart TD
    Z[xml.zip<br/>gesetze-im-internet.de] --> P[XML parsen<br/>809 norm-Elemente]
    P --> F{§-Norm<br/>mit Text?}
    F -->|nein| X[verworfen<br/>27 Paragraphen]
    F -->|ja| A[nach Absätzen teilen]
    A --> W{Absatz<br/>weggefallen?}
    W -->|ja| Y[übersprungen<br/>99 Absätze]
    W -->|nein| L{> 3000<br/>Zeichen?}
    L -->|ja| S[an Satzgrenzen teilen<br/>200 Zeichen Überlappung]
    L -->|nein| C[Chunk]
    S --> C
    C --> H[Überschrift voranstellen]
    H --> E[bge-m3 Embedding]
    E --> DB[(Chroma<br/>cosine)]

    FAQ[faq.yaml<br/>18 Einträge] --> E

    style DB fill:#0f766e,color:#fff
    style X fill:#7f1d1d,color:#fff
    style Y fill:#7f1d1d,color:#fff
```

## Warum diese Bausteine

| Baustein | Wahl | Grund |
|---|---|---|
| Embedding | `bge-m3` | mehrsprachig, deutscher Korpus → [002](entscheidungen/002-embedding-modell.md) |
| Generierung | `llama3.2:3b` | läuft nativ auf dem Mac mit GPU, 2 GB |
| Vektorspeicher | ChromaDB | eingebettet, keine eigene Instanz nötig |
| Distanzmaß | Kosinus | Standard für Satz-Embeddings; Chroma-Default ist L2 |
| Paketmanager | uv | schnell, sperrt Versionen, verwaltet die Python-Version |

## Konfiguration

Sämtliche Einstellungen kommen aus Environment-Variablen, damit im Container
nichts angefasst werden muss (`src/health_faq_agent/config.py`):

| Variable | Default |
|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` |
| `EMBEDDING_MODEL` | `bge-m3` |
| `CHAT_MODEL` | `llama3.2:3b` |
| `CHROMA_PATH` | `data/chroma` |
| `CHROMA_COLLECTION` | `sgb5` |
| `DATA_RAW_DIR` | `data/raw` |

!!! warning "Modellwechsel erzwingt Neuindexierung"
    Unterschiedliche Embedding-Modelle erzeugen unterschiedliche Dimensionen
    und liegen in unterschiedlichen Vektorräumen. Nach einer Änderung von
    `EMBEDDING_MODEL` muss `ingest_sgb5.py --rebuild` laufen.
