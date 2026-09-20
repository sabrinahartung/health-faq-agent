# Entwicklung

## Voraussetzungen

- Python 3.12 (wird von uv über `.python-version` bereitgestellt)
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com), nativ installiert

!!! warning "Ollama nativ, nicht im Container"
    Im Container hat Ollama auf dem Mac keinen GPU-Zugriff. Aus dem Container
    heraus wird später auf `host.docker.internal:11434` gezeigt.

## Einrichten

```bash
git clone https://github.com/sabrinahartung/health-faq-agent.git
cd health-faq-agent

uv sync

ollama pull llama3.2:3b
ollama pull bge-m3
```

## Korpus aufbauen

```bash
# SGB V laden, chunken, einbetten (~80 s)
uv run scripts/ingest_sgb5.py --rebuild

# FAQ-Ebene darüberlegen
uv run scripts/ingest_faq.py
```

Nützliche Schalter:

| Aufruf | Wirkung |
|---|---|
| `--dry-run` | nur parsen und chunken, nichts einbetten |
| `--limit 20` | nur die ersten 20 Chunks |
| `--max-chars 2000` | andere Chunk-Größe ausprobieren |
| `--refresh` | XML neu laden statt aus dem Cache |
| `-v` | ausführliches Log |

## Messen

```bash
uv run scripts/eval_retrieval.py --ohne-faq
uv run scripts/eval_retrieval.py
uv run scripts/eval_retrieval.py --details
```

## Dokumentation

```bash
# lokal unter http://127.0.0.1:8000, lädt bei Änderungen neu
uv run mkdocs serve

# statisch bauen
uv run mkdocs build --strict
```

Ein Push auf `main` baut und veröffentlicht die Seite automatisch nach
GitHub Pages.

!!! note "Einmalig im Repository einstellen"
    **Settings → Pages → Build and deployment → Source: GitHub Actions.**
    Ohne diese Einstellung läuft der Workflow, aber nichts wird veröffentlicht.

## Projektstruktur

```
health-faq-agent/
├── data/
│   ├── eval/golden_set.yaml     # Testmenge — NIE indexieren
│   ├── faq/faq.yaml             # FAQ-Ebene — wird indexiert
│   ├── chroma/                  # Vektorspeicher (gitignored)
│   └── raw/                     # heruntergeladenes XML (gitignored)
├── docs/                        # diese Dokumentation
├── scripts/
│   ├── ingest_sgb5.py
│   ├── ingest_faq.py
│   └── eval_retrieval.py
├── src/health_faq_agent/
│   └── config.py                # Environment-Variablen
├── mkdocs.yml
└── pyproject.toml
```

## Konventionen

- **Konfiguration nur über Environment-Variablen**, nie hartkodiert.
- **Jede nennenswerte Entscheidung** bekommt eine Notiz unter
  `docs/entscheidungen/`.
- **Irrwege bleiben dokumentiert.** Der Ingest-Bug in
  [003](entscheidungen/003-chunking.md) ist Teil der Geschichte, nicht
  ihr Schönheitsfehler.
