# Entscheidungen

Kurze Notizen zu Entscheidungen, die den Verlauf des Projekts geprägt haben —
nach dem Muster von *Architecture Decision Records*. Jede Notiz hält fest,
**was** entschieden wurde, **warum**, und **was dagegen sprach**.

Der Sinn ist nicht Vollständigkeit, sondern Nachvollziehbarkeit: in drei
Monaten soll rekonstruierbar sein, warum etwas so aussieht, wie es aussieht.
Überholte Entscheidungen werden nicht gelöscht, sondern als *überholt*
markiert und verlinkt.

| Nr. | Titel | Datum | Status |
|---|---|---|---|
| [001](001-korpus.md) | SGB V als Korpus | 2026-09-20 | angenommen |
| [002](002-embedding-modell.md) | bge-m3 statt nomic-embed-text | 2026-09-20 | angenommen |
| [003](003-chunking.md) | Chunking nach Absätzen | 2026-09-20 | angenommen |
| [004](004-faq-ebene.md) | Handgeschriebene FAQ-Ebene | 2026-09-20 | angenommen |

## Vorlage

```markdown
# NNN — Titel

**Datum:** JJJJ-MM-TT · **Status:** vorgeschlagen | angenommen | überholt

## Kontext
Welche Situation erzwingt eine Entscheidung?

## Entscheidung
Was wird getan?

## Begründung
Warum dieser Weg?

## Verworfene Alternativen
Was wurde geprüft und aus welchem Grund verworfen?

## Konsequenzen
Was wird dadurch leichter, was schwerer?
```
