# Datenquellen

Der Korpus wird **nicht** im Repository versioniert. `scripts/ingest_sgb5.py`
laedt ihn reproduzierbar nach `data/raw/` (per `.gitignore` ausgeschlossen).

## SGB V — Gesetzliche Krankenversicherung

| | |
|---|---|
| Quelle | https://www.gesetze-im-internet.de/sgb_5/ |
| Bulk-Download | https://www.gesetze-im-internet.de/sgb_5/xml.zip (609 KB) |
| Herausgeber | Bundesministerium der Justiz / Bundesamt fuer Justiz |
| Stand | `builddate` im XML, beim Ingest protokolliert |
| Umfang | 694 Paragraphen, davon 591 mit Text → 2501 Chunks |

**Rechtsgrundlage der Nutzung:** Nach § 5 Abs. 1 UrhG geniessen Gesetze keinen
urheberrechtlichen Schutz. Der Normtext ist damit frei verwendbar.

**Einschraenkung:** Die *konsolidierte Fassung* und die XML-Aufbereitung stammen
vom Bundesamt fuer Justiz in Zusammenarbeit mit der juris GmbH. Das Archiv wird
deshalb nicht weiterverbreitet, sondern zur Laufzeit geladen. Abgeleitete
Textabschnitte im Index sind davon nicht betroffen.

**Amtlichkeit:** gesetze-im-internet.de stellt *nicht amtliche* konsolidierte
Fassungen bereit. Verbindlich ist allein das Bundesgesetzblatt. Der Agent gibt
darum in jeder Antwort die Fundstelle an, statt Verbindlichkeit zu suggerieren.

## Eigene FAQ-Ebene

`data/faq/` enthaelt handgeschriebene deutschsprachige Frage-Antwort-Paare mit
Verweis auf den jeweiligen Paragraphen. Vollstaendig selbst verfasst, faellt
unter die MIT-Lizenz dieses Repositories und wird mitversioniert.

## Bewusst nicht genutzt

- **Krankenkassen-FAQ (TK, AOK, Barmer):** urheberrechtlich geschuetzt.
- **gesund.bund.de:** Inhalte des BMG, kein `robots.txt` und keine
  Nutzungslizenz hinterlegt — kein belastbares Recht zur Weiterverwendung.

## Nicht-Ziel

Keine Patientendaten, keine personenbezogenen Daten, keine medizinische
Einzelfallberatung. Der Korpus besteht ausschliesslich aus oeffentlichem
Normtext zu Leistungsansprüchen.
