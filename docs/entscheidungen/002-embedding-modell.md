# 002 — bge-m3 statt nomic-embed-text

**Datum:** 2026-09-20 · **Status:** angenommen

## Kontext

Der ursprüngliche Plan nannte `nomic-embed-text`. Das ist der De-facto-Default
im Ollama-Ökosystem: ein BERT-artiger Encoder (rund 137 M Parameter) mit
Rotary Embeddings und 8192 Token Kontext, kontrastiv auf etwa 235 Millionen
Textpaaren nachtrainiert, Apache-2.0 inklusive offener Trainingsdaten.

Der Unterschied zu einem rohen BERT liegt nicht im Aufbau, sondern im
Trainingsziel: BERT wurde auf Masked Language Modelling trainiert, seine
Vektoren eignen sich kaum für Ähnlichkeitssuche. Erst kontrastives
Nachtrainieren macht daraus ein Retrieval-Modell.

**Das Problem:** `nomic-embed-text` v1.5 ist englischsprachig trainiert. Der
Korpus dieses Projekts ist durchgehend deutsch.

## Entscheidung

`bge-m3` (BAAI, 567 M Parameter, 1024 Dimensionen, 8k Kontext) als
Embedding-Modell — konfigurierbar über `EMBEDDING_MODEL`.

## Begründung

- Explizit mehrsprachig trainiert, deutsches Retrieval ist kein Nebenprodukt.
- 8k Kontext, damit passen auch lange Paragraphen ungeteilt.
- Braucht **keine Task-Prefixe**. `nomic-embed-text` erwartet
  `search_document:` und `search_query:`; Ollama setzt diese nicht
  automatisch, und ohne sie sinkt die Qualität spürbar. Eine Fehlerquelle,
  die in den meisten Tutorials übersehen wird.
- In Ollama verfügbar, 1,2 GB, läuft lokal.

## Verworfene Alternativen

| Modell | Grund |
|---|---|
| `nomic-embed-text` | englischlastig, Prefix-Falle |
| `nomic-embed-text-v2-moe` | mehrsprachig, aber weniger erprobt |
| `embeddinggemma` | kleiner, aber 768 Dim und kürzerer Kontext |
| `mxbai-embed-large` | stark im Englischen, nicht mehrsprachig |

## Konsequenzen

`EMBEDDING_MODEL` ist von Beginn an eine Environment-Variable — ein Wechsel
erzwingt vollständige Neuindexierung, weil Dimension und Vektorraum sich
ändern.

**Noch offen:** ein direkter Vergleich `bge-m3` gegen `nomic-embed-text` auf
dem Golden Set. Das Messwerkzeug steht bereits
(`scripts/eval_retrieval.py`), der Vergleich fehlt.
