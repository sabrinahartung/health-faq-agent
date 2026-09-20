# 003 — Chunking nach Absätzen

**Datum:** 2026-09-20 · **Status:** angenommen

## Kontext

Die Paragraphen des SGB V sind extrem ungleich lang: der Median liegt bei
etwa 1 900 Zeichen, das 90. Perzentil bei 8 000, der längste Paragraph
(§ 87) bei über 55 000 Zeichen. Ein Paragraph pro Chunk wäre unbrauchbar,
ein fixes Zeichenfenster zerschneidet Sinneinheiten.

## Entscheidung

Drei Stufen:

1. **Nach Absätzen teilen.** Absatzmarker `(1)`, `(2)`, `(2a)` am
   Zeilenanfang erzeugen jeweils einen Chunk.
2. **Zu lange Absätze an Satzgrenzen nachteilen**, Standard 3 000 Zeichen mit
   200 Zeichen Überlappung.
3. **Überschrift voranstellen.** Jeder Chunk beginnt mit
   `§ 27 Krankenbehandlung (SGB V), Absatz 1`.

Ergebnis: **3 002 Chunks**, Median 656 Zeichen.

## Begründung

Der Absatz ist die natürliche Sinneinheit des Gesetzestextes — und zugleich
die übliche Zitiereinheit. Ein Chunk entspricht damit genau einer Fundstelle
(`§ 39 Abs. 4 SGB V`), was das Antwortschema aus Phase 1 direkt bedient.

Die vorangestellte Überschrift ist kein Schmuck. Ohne sie sieht `bge-m3` nur
nackten Normtext; der thematische Bezug — worum es in diesem Paragraphen
überhaupt geht — fehlt im Vektor.

## Fallstricke im Quell-XML

**Aufzählungen kleben zusammen.** Marker und Text stehen in getrennten
`<DT>`/`<DD>`-Elementen. Naives `itertext()` erzeugt
`umfaßt 1.Ärztliche Behandlung 2.zahnärztliche` — der Renderer läuft deshalb
über die Paare und setzt Umbrüche.

**`(weggefallen)` — ein teurer Fehler.** Aufgehobene Absätze tragen den Text
`(weggefallen)`. Die erste Fassung des Skripts prüfte das auf Ebene des
*Paragraphen*:

```python
if not body or "(weggefallen)" in body:
    continue          # verwirft den GANZEN Paragraphen
```

Damit verschwanden **71 gültige Paragraphen**, darunter § 39
(Krankenhausbehandlung), § 31 (Arzneimittel) und § 35 (Festbeträge) — jeder
von ihnen enthält irgendwo einen einzelnen aufgehobenen Absatz.

Aufgefallen ist es nur, weil eine Testfrage nach der Krankenhaus-Zuzahlung
den falschen Paragraphen lieferte und die Nachfrage `where={"paragraph_nr":
"39"}` eine leere Liste zurückgab. Die Korrektur filtert je Absatz:

```python
kern = ABSATZ_RE.sub("", abs_text).strip()
if not kern or kern == "(weggefallen)":
    dropped_absaetze += 1
    continue          # nur DIESEN Absatz überspringen
```

**501 Chunks mehr**, und § 39 Abs. 4 landet für die Krankenhaus-Frage auf
Rang 2 statt gar nicht im Index.

!!! note "Lehre"
    Ein stiller Datenverlust im Ingest sieht aus wie schlechtes Retrieval.
    Deshalb protokolliert das Skript jetzt, wie viele Paragraphen und wie
    viele Absätze es verwirft — eine Zahl, die man beim Lesen stutzig macht,
    ist mehr wert als ein stilles `continue`.

## Konsequenzen

Chunk-Größe, Überlappung und Batch-Größe sind CLI-Parameter
(`--max-chars`, `--overlap`, `--batch-size`) und lassen sich gegen
`eval_retrieval.py` durchprobieren, ohne den Code anzufassen.
