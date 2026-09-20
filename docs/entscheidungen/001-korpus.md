# 001 — SGB V als Korpus

**Datum:** 2026-09-20 · **Status:** angenommen

## Kontext

Der Plan sah „öffentliche Gesundheits-FAQ oder Leistungsinformationen" vor,
ohne Quelle. Zwei Anforderungen standen im Konflikt:

1. Der Korpus soll thematisch zu einer Krankenkasse passen.
2. Das Repository soll öffentlich sein — der Inhalt muss also rechtlich
   unbedenklich weiterverwendbar sein.

Genau daran scheitern die naheliegenden Quellen: die FAQ-Seiten von TK, AOK
oder Barmer sind thematisch perfekt und urheberrechtlich geschützt.

## Entscheidung

Primärkorpus ist das **Sozialgesetzbuch Fünftes Buch (SGB V)**, bezogen als
XML-Gesamtausgabe von `gesetze-im-internet.de`.

Der Korpus wird **nicht** im Repository versioniert. `scripts/ingest_sgb5.py`
lädt ihn reproduzierbar nach `data/raw/`, das per `.gitignore` ausgeschlossen
ist. Versioniert werden das Skript und die Quellenangabe.

## Begründung

**Rechtlich eindeutig.** Nach § 5 Abs. 1 UrhG genießen Gesetze keinen
urheberrechtlichen Schutz.

**Thematisch am Ursprung.** Das Dritte Kapitel heißt wörtlich „Leistungen der
Krankenversicherung" — die im Plan gesuchten Leistungsinformationen, an der
Quelle statt in einer Sekundärdarstellung.

**Technisch sauber.** Ein Download von 609 KB, 809 strukturierte
`<norm>`-Elemente mit Paragraphennummer und Überschrift. Kein Scraping, keine
`robots.txt`-Grauzone, kein Rate-Limiting.

**Zitierfähig von Haus aus.** Jeder Chunk trägt eine natürliche Fundstelle
(`§ 27 Abs. 1 SGB V`). Das Antwortschema aus Phase 1 bekommt seine
Quellenangaben geschenkt.

**Der Scope wird dadurch schärfer.** „Gesundheits-FAQ" ist unscharf, und
unscharfer Scope macht die Ablehnungsfälle der Evaluation beliebig. Mit dem
SGB V ergibt sich eine begründbare Grenze:

> Beantwortet werden Fragen zu **Ansprüchen, Leistungen und Zuzahlungen**.
> Nicht beantwortet werden Fragen zum **medizinischen Einzelfall**.

## Verworfene Alternativen

| Quelle | Grund |
|---|---|
| TK-, AOK-, Barmer-FAQ | urheberrechtlich geschützt, nicht weiterverbreitbar |
| gesund.bund.de | BMG-Inhalte, keine `robots.txt`, keine Nutzungslizenz hinterlegt |
| IQWiG / gesundheitsinformation.de | hochwertig, aber geschützt |
| Wikipedia (CC BY-SA) | frei, aber keine Leistungs- oder Anspruchsinformationen |

## Konsequenzen

**Leichter:** Lizenzfragen, Zitierbarkeit, Reproduzierbarkeit, Scope-Definition.

**Schwerer:** Gesetzessprache liegt weit von Alltagssprache entfernt. Das hat
messbare Folgen fürs Retrieval und führte direkt zu
[Entscheidung 004](004-faq-ebene.md).

**Offene Flanke:** Gesetzestext ist eine Kette von Verweisen. § 39 Abs. 4
nennt den Zuzahlungsbetrag nicht, sondern verweist auf § 61 Satz 2. RAG folgt
Verweisen nicht. Einzelne Antworten brauchen deshalb zwei Chunks gleichzeitig.
