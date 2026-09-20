# 004 — Handgeschriebene FAQ-Ebene

**Datum:** 2026-09-20 · **Status:** angenommen

## Kontext

Nach dem ersten vollständigen Index lieferte das Retrieval auf umgangssprachliche
Fragen gemischte Ergebnisse. Der aufschlussreichste Fehlschlag:

> **Frage:** „Bin ich als **Studentin** bei meinen **Eltern mitversichert**?"

| Treffer | Warum |
|---|---|
| **Rang 1** — § 199a *Informationspflichten bei krankenversicherten **Studenten*** | teilt ein Wort |
| **Rang 4** — § 10 *Familienversicherung* | teilt **kein** Wort |

§ 10 ist die richtige Antwort. Er sagt nie *Studentin*, nie *mitversichert*,
nie *Eltern* — er sagt *Kinder von Mitgliedern*.

## Die Diagnose

Ein Embedding-Modell misst nicht „beantwortet dieser Text diese Frage", sondern
„ähneln sich diese beiden Texte". Das ist nicht dasselbe. Frage und Antwort
sind in unterschiedlichen Registern geschrieben, von unterschiedlichen Menschen,
zu unterschiedlichen Zwecken. In der Literatur heißt das
**Query-Document-Asymmetrie**.

Dazu kommen zwei Eigenschaften des Korpus:

- **Gesetzestext ist eine Kette.** § 39 Abs. 4 nennt den Betrag nicht, sondern
  verweist auf § 61 Satz 2. RAG holt Chunks, es folgt keinen Verweisen.
- **Das Gesetz nennt Ansprüche, keine Fälle.** „Meine Tochter ist 20 und
  arbeitet nicht" verlangt die *Anwendung* von § 10 Abs. 2 Nr. 2.

Auffällig war außerdem die **enge Distanzspanne**: über die gesamten Top 20
lagen die Kosinus-Distanzen zwischen 0,386 und 0,494. Alle Chunks teilen
dieselbe juristische Fachsprache, die Trennschärfe ist entsprechend gering.

## Entscheidung

Eine zweite, handgeschriebene Ebene in `data/faq/faq.yaml`: 18 Einträge mit
insgesamt 72 Formulierungen. Jeder Eintrag bündelt eine Alltagsfrage, mehrere
Paraphrasen, eine kurze Antwort in Alltagssprache und die Fundstelle.

Alle Formulierungen eines Eintrags landen in **einem** Dokument. Der Vektor
liegt damit in der Mitte der Paraphrasen und trifft ein breiteres Spektrum,
ohne die Trefferliste mit Dubletten desselben Eintrags zu fluten.

Die Ebene liegt in **derselben** Collection wie der Normtext, markiert mit
`typ: faq`. Eine Anfrage trifft beide; über das Metadatenfeld lässt sich die
Ebene für Vergleichsmessungen ausblenden.

## Wirkung

22 beantwortbare Fragen aus dem Golden Set:

| | nur SGB V | + FAQ-Ebene |
|---|---|---|
| Recall@1 | 68 % | **95 %** |
| Recall@3 | 77 % | **95 %** |
| Recall@5 | 86 % | **100 %** |
| mittlerer Rang | 1,7 | **1,1** |

!!! warning "Diese Zahl ist optimistisch"
    Die FAQ-Einträge wurden in Kenntnis der Themen des Golden Sets verfasst.
    Die *Formulierungen* unterscheiden sich bewusst, die *Themen* überschneiden
    sich. Eine faire Messung braucht Golden-Fragen zu Themen, die die FAQ-Ebene
    nicht abdeckt. Die 100 % sind ein Zwischenstand, kein Gütesiegel.

## Verworfene Alternativen

| Ansatz | Grund |
|---|---|
| Jede Paraphrase als eigener Chunk | flutet die Trefferliste mit Dubletten |
| Reranker (`bge-reranker-v2-m3`) | wirksam, aber teurer — erst messen, dann bauen |
| Hybride Suche (BM25 + dense) | dito; sinnvoll, wenn die FAQ-Ebene ausgereizt ist |
| Größeres LLM statt besserem Retrieval | behebt die Ursache nicht |

## Konsequenzen

Die FAQ-Ebene ist **Teil des Systems**, nicht der Evaluation. Ihr Gegenstück,
`data/eval/golden_set.yaml`, wird **niemals** indexiert — siehe
[Evaluation](../evaluation.md).
