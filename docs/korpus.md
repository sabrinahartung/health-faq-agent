# Korpus & Lizenz

Der Korpus wird **nicht** im Repository versioniert. `scripts/ingest_sgb5.py`
lädt ihn reproduzierbar nach `data/raw/`, das per `.gitignore` ausgeschlossen
ist. Versioniert werden das Skript und diese Seite.

## SGB V — Gesetzliche Krankenversicherung

| | |
|---|---|
| Quelle | <https://www.gesetze-im-internet.de/sgb_5/> |
| Bulk-Download | `https://www.gesetze-im-internet.de/sgb_5/xml.zip` (609 KB) |
| Herausgeber | Bundesministerium der Justiz / Bundesamt für Justiz |
| Stand | `builddate` im XML, beim Ingest protokolliert |
| Umfang | 809 `<norm>`-Elemente → 3 002 Chunks |

**Rechtsgrundlage:** Nach § 5 Abs. 1 UrhG genießen Gesetze keinen
urheberrechtlichen Schutz.

**Einschränkung:** Die *konsolidierte Fassung* und die XML-Aufbereitung
stammen vom Bundesamt für Justiz in Zusammenarbeit mit der juris GmbH. Das
Archiv wird deshalb nicht weiterverbreitet, sondern zur Laufzeit geladen.
Abgeleitete Textabschnitte im Index sind davon nicht betroffen.

**Amtlichkeit:** `gesetze-im-internet.de` stellt *nicht amtliche*
konsolidierte Fassungen bereit. Verbindlich ist allein das Bundesgesetzblatt.
Der Agent gibt darum in jeder Antwort die Fundstelle an, statt Verbindlichkeit
zu suggerieren.

## Eigene FAQ-Ebene

`data/faq/faq.yaml` enthält handgeschriebene deutschsprachige
Frage-Antwort-Paare mit Verweis auf den jeweiligen Paragraphen. Vollständig
selbst verfasst, fällt unter die MIT-Lizenz dieses Repositories und wird
mitversioniert. Begründung siehe
[Entscheidung 004](entscheidungen/004-faq-ebene.md).

Alle Antworten sind gegen den Normtext geprüft. Beträge und Fristen ändern
sich — vor Übernahme gegenprüfen.

## Bewusst nicht genutzt

| Quelle | Grund |
|---|---|
| Krankenkassen-FAQ (TK, AOK, Barmer) | urheberrechtlich geschützt |
| gesund.bund.de | BMG-Inhalte, keine `robots.txt`, keine Nutzungslizenz hinterlegt |
| IQWiG / gesundheitsinformation.de | hochwertig, aber geschützt |

## Nicht-Ziel

Keine Patientendaten, keine personenbezogenen Daten, keine medizinische
Einzelfallberatung. Der Korpus besteht ausschließlich aus öffentlichem
Normtext zu Leistungsansprüchen.
