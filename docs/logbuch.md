# Logbuch

Chronologisch, knapp, mit Irrwegen. Neue Einträge kommen oben dazu.

---

## 2026-09-20 — Dokumentation aufgesetzt

MkDocs mit Material-Theme, Deployment nach GitHub Pages über Actions.
Entscheidungen werden ab jetzt als nummerierte Notizen mitgeschrieben,
statt am Ende rekonstruiert zu werden.

## 2026-09-20 — FAQ-Ebene und Golden Set

18 FAQ-Einträge mit 72 Formulierungen, 33 Golden-Fragen in drei Kategorien.
Gemessene Wirkung: Recall@1 von 68 % auf 95 %.

Wichtigste Einsicht des Tages: **Ein Embedding-Modell misst Textähnlichkeit,
nicht Antwortrelevanz.** § 199a gewann gegen § 10, weil im Titel das Wort
„Studenten" steht — obwohl § 10 die Frage beantwortet und § 199a nicht.

Zweite Einsicht: FAQ-Ebene und Golden Set dürfen nie dieselbe Datei sein.
Details unter [Evaluation](evaluation.md).

## 2026-09-20 — Bug: 71 Paragraphen still verloren

Die Prüfung `if "(weggefallen)" in body` verwarf den **gesamten** Paragraphen,
sobald ein einzelner Absatz aufgehoben war. Betroffen: 71 gültige Paragraphen,
darunter § 39 (Krankenhausbehandlung), § 31 (Arzneimittel), § 35.

Aufgefallen beim Gegenlesen eines Retrieval-Ergebnisses, nicht durch einen
Test. `where={"paragraph_nr": "39"}` lieferte eine leere Liste.

Korrektur: Filter je Absatz statt je Paragraph. 2 501 → **3 002 Chunks**.
Das Skript protokolliert seitdem verworfene Paragraphen und Absätze getrennt.
Ausführlich in [Entscheidung 003](entscheidungen/003-chunking.md).

## 2026-09-20 — Korpus festgelegt und indexiert

SGB V als XML von `gesetze-im-internet.de`, Chunking nach Absätzen,
Embeddings über `bge-m3`. Erster vollständiger Index in 80 Sekunden.

Erste Retrieval-Stichprobe: 2 von 5 Alltagsfragen sauber getroffen. Nicht
gut genug — Auslöser für die Analyse, die zur FAQ-Ebene führte.

## 2026-09-20 — Embedding-Modell gewechselt

`nomic-embed-text` (Plan) durch `bge-m3` ersetzt: der Korpus ist deutsch, das
Modell im Plan englischsprachig trainiert. Begründung unter
[Entscheidung 002](entscheidungen/002-embedding-modell.md).

## 2026-09-20 — Projektstruktur begradigt

`uv init health-faq-agent` hatte ein Projektverzeichnis **innerhalb** des
bereits initialisierten Repositories angelegt, parallel dazu existierte ein
von PyCharm erzeugtes `.venv` mit Python 3.13 neben dem von uv gepinnten 3.12.

Da noch kein Commit existierte, war das Flachziehen kostenlos: Projektdateien
eine Ebene hoch, beide venvs verworfen, `uv sync` neu, `.gitignore` ergänzt.

!!! tip "Nebenbei gelernt"
    In PyCharm heißt ein venv-basierter Interpreter `Python 3.12 (Projektname)`.
    Ein nacktes `Python 3.12` ohne Klammerzusatz zeigt auf einen System- oder
    Basis-Interpreter — im Zweifel prüfen mit
    `import sys; print(sys.executable)` in der Python-Konsole.
