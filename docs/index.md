# Health-FAQ-Agent

Ein RAG-Agent, der Fragen zu **Leistungsansprüchen der gesetzlichen
Krankenversicherung** beantwortet — mit Fundstelle im Gesetz, vollständig
lokal, ohne einen einzigen API-Schlüssel.

!!! info "Scope"
    Der Agent beantwortet Fragen zu **Ansprüchen, Leistungen und Zuzahlungen**.
    Er gibt **keine medizinische Einzelfallberatung**. Diese Grenze ist nicht
    nachträglich aufgesetzt, sondern folgt aus der Wahl des Korpus — siehe
    [Entscheidung 001](entscheidungen/001-korpus.md).

## Warum es diesen Dienst gibt

Das Projekt ist eine Lernstrecke entlang eines realen Stellenprofils: ein
Agenten-Service, der nicht nur funktioniert, sondern beobachtbar, bewertet
und nachvollziehbar ist. Was hier dokumentiert wird, ist deshalb nicht nur
das Ergebnis, sondern der Weg dahin — inklusive der Irrwege.

## Stand

| Phase | Inhalt | Status |
|---|---|---|
| 0 | Setup, Toolchain, lokale Modelle | ✅ abgeschlossen |
| 0 | Korpus festgelegt und indexiert | ✅ abgeschlossen |
| 1 | FastAPI-Service, Agent mit Tools | 🔨 in Arbeit |
| 2 | Container, Compose, Podman | ⬜ offen |
| 3 | Langfuse, Prometheus, Grafana | ⬜ offen |
| 4 | Golden Set, LLM-as-a-Judge, Refusal-Rate | 🔨 Grundlage steht |
| 5 | CI/CD | 🔨 Docs-Deployment steht |
| 6 | Kubernetes (optional) | ⬜ offen |
| 7 | README, Diagramme, Vortrag | ⬜ offen |

## Kennzahlen heute

<div class="grid cards" markdown>

-   **3 002**{ .lg } Chunks

    ---

    Normtext des SGB V, nach Absätzen geschnitten

-   **18**{ .lg } FAQ-Einträge

    ---

    72 Alltagsformulierungen als Brücke zur Gesetzessprache

-   **95 %**{ .lg } Recall@1

    ---

    gegen 68 % ohne FAQ-Ebene → [Evaluation](evaluation.md)

-   **0 €**{ .lg } Laufkosten

    ---

    Ollama, Chroma, Langfuse und Grafana laufen lokal

</div>

## Schnellstart

```bash
# Modelle bereitstellen
ollama pull llama3.2:3b
ollama pull bge-m3

# Abhängigkeiten
uv sync

# Korpus laden und indexieren
uv run scripts/ingest_sgb5.py --rebuild
uv run scripts/ingest_faq.py

# Retrieval prüfen
uv run scripts/eval_retrieval.py
```

Mehr dazu unter [Entwicklung](entwicklung.md).

## Haftungsausschluss

Die verwendeten Gesetzestexte sind **nicht amtliche** konsolidierte Fassungen.
Verbindlich ist allein das Bundesgesetzblatt. Der Agent nennt deshalb in jeder
Antwort die Fundstelle, statt Verbindlichkeit zu suggerieren.
