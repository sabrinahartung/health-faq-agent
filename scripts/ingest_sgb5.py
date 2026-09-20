#!/usr/bin/env python3
"""Ingest des SGB V (Gesetzliche Krankenversicherung) in ChromaDB.

Quelle:  https://www.gesetze-im-internet.de/sgb_5/xml.zip
Lizenz:  Der Normtext ist nach § 5 UrhG nicht urheberrechtlich geschuetzt.
         Details und Stand siehe SOURCES.md.

Ablauf:  XML laden (gecached) -> Normen parsen -> nach Absaetzen chunken
         -> ueber Ollama einbetten -> in eine Chroma-Collection upserten.

Die Chunk-IDs sind deterministisch, der Lauf ist damit idempotent:
ein erneuter Aufruf aktualisiert bestehende Chunks, statt zu duplizieren.

Beispiele:
    uv run scripts/ingest_sgb5.py
    uv run scripts/ingest_sgb5.py --rebuild
    uv run scripts/ingest_sgb5.py --dry-run --limit 20
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from health_faq_agent.config import Settings

XML_URL = "https://www.gesetze-im-internet.de/sgb_5/xml.zip"
NORM_URL = "https://www.gesetze-im-internet.de/sgb_5/__{num}.html"

# Absatzmarker am Zeilenanfang: (1), (2), (2a) ...
ABSATZ_RE = re.compile(r"^\((\d+[a-z]?)\)\s*")
# "§ 27a" -> "27a"
PARA_RE = re.compile(r"^§+\s*([\d]+[a-z]?)")
# Satzgrenzen fuer das Nachchunken sehr langer Absaetze
SENTENCE_RE = re.compile(r"(?<=[.;:])\s+")

log = logging.getLogger("ingest")


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------- download


def fetch_xml(raw_dir: Path, force: bool = False) -> Path:
    """Laedt xml.zip und entpackt es nach raw_dir. Nutzt den Cache."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / "sgb5.zip"

    if force or not archive.exists():
        log.info("lade %s", XML_URL)
        req = urllib.request.Request(
            XML_URL, headers={"User-Agent": "health-faq-agent/0.1 (Lernprojekt)"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp, archive.open("wb") as fh:
            fh.write(resp.read())
        log.info("gespeichert: %s (%.1f KB)", archive, archive.stat().st_size / 1024)
    else:
        log.info("nutze Cache: %s (--refresh erzwingt Neuladen)", archive)

    with zipfile.ZipFile(archive) as zf:
        names = [n for n in zf.namelist() if n.endswith(".xml")]
        if not names:
            raise RuntimeError(f"keine XML-Datei in {archive}")
        target = raw_dir / names[0]
        if force or not target.exists():
            zf.extract(names[0], raw_dir)
    return target


# ------------------------------------------------------------------ parse


def _inline(el: ET.Element) -> str:
    """Element inklusive verschachtelter Tags zu einer Zeile flachdruecken."""
    return " ".join("".join(el.itertext()).split())


def _render_list(dl: ET.Element) -> str:
    """<DL> mit DT/DD-Paaren als eingerueckte Aufzaehlung rendern.

    Ohne dieses Trennen klebt im Quell-XML der Marker am Text
    ("umfasst 1.Aerztliche Behandlung 2.zahnaerztliche ...").
    """
    items, marker = [], ""
    for el in dl:
        if el.tag == "DT":
            marker = _inline(el)
        elif el.tag == "DD":
            body = _inline(el)
            if body:
                items.append(f"{marker} {body}".strip())
            marker = ""
    return "\n".join(f"  {item}" for item in items)


def render_text(content: ET.Element) -> str:
    """<Content> zu Klartext rendern, eine Zeile je Block."""
    blocks = []
    for el in content:
        block = _render_list(el) if el.tag == "DL" else _inline(el)
        if block:
            blocks.append(block)
    return "\n".join(blocks)


def split_absaetze(text: str) -> list[tuple[str | None, str]]:
    """Text an Absatzmarkern ((1), (2), ...) aufteilen."""
    buckets: list[tuple[str | None, list[str]]] = []
    for line in text.split("\n"):
        match = ABSATZ_RE.match(line)
        if match:
            buckets.append((match.group(1), [line]))
        elif buckets:
            buckets[-1][1].append(line)
        else:
            # Text vor dem ersten Absatzmarker (einabsaetzige Paragraphen)
            buckets.append((None, [line]))
    return [(nr, "\n".join(lines).strip()) for nr, lines in buckets if "\n".join(lines).strip()]


def split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Sehr lange Absaetze an Satzgrenzen teilen, mit Ueberlappung."""
    if len(text) <= max_chars:
        return [text]

    parts: list[str] = []
    current = ""
    for sentence in SENTENCE_RE.split(text):
        if current and len(current) + len(sentence) + 1 > max_chars:
            parts.append(current.strip())
            tail = current[-overlap:] if overlap else ""
            current = f"{tail} {sentence}" if tail else sentence
        else:
            current = f"{current} {sentence}".strip()
    if current.strip():
        parts.append(current.strip())
    return parts


def build_chunks(xml_path: Path, max_chars: int, overlap: int) -> list[Chunk]:
    root = ET.parse(xml_path).getroot()
    chunks: list[Chunk] = []
    skipped = 0

    for norm in root.findall(".//norm"):
        enbez = (norm.findtext(".//enbez") or "").strip()
        para = PARA_RE.match(enbez)
        if not para:
            # Kapitel- und Abschnittsueberschriften, Rahmennorm, Anlagen
            continue

        num = para.group(1)
        titel = (norm.findtext(".//titel") or "").strip()
        content = norm.find(".//textdaten/text/Content")
        body = render_text(content) if content is not None else ""

        if not body or "(weggefallen)" in body:
            skipped += 1
            continue

        absaetze = split_absaetze(body)
        for abs_nr, abs_text in absaetze:
            parts = split_long(abs_text, max_chars, overlap)
            for i, part in enumerate(parts):
                # Ueberschrift voranstellen: bge-m3 sieht sonst nur nackten
                # Normtext und verliert den Bezug zum Thema des Paragraphen.
                header = f"{enbez} {titel} (SGB V)".strip()
                if abs_nr:
                    header += f", Absatz {abs_nr}"

                meta = {
                    "gesetz": "SGB V",
                    "paragraph": enbez,
                    "paragraph_nr": num,
                    "titel": titel,
                    "absatz": abs_nr or "",
                    "teil": i,
                    "teile_gesamt": len(parts),
                    "zitat": f"{enbez}{f' Abs. {abs_nr}' if abs_nr else ''} SGB V",
                    "source_url": NORM_URL.format(num=num),
                }
                chunks.append(
                    Chunk(
                        id=f"sgb5-{num}-{abs_nr or '0'}-{i}",
                        text=f"{header}\n{part}",
                        metadata=meta,
                    )
                )

    log.info("%d Chunks aus %s (%d Paragraphen weggefallen/leer)", len(chunks), xml_path.name, skipped)
    return chunks


# ------------------------------------------------------------------ index


def index(chunks: list[Chunk], settings: Settings, batch_size: int, rebuild: bool) -> None:
    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

    embed = OllamaEmbeddingFunction(url=settings.ollama_host, model_name=settings.embedding_model)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_path))

    if rebuild:
        try:
            client.delete_collection(settings.collection)
            log.info("Collection %r geloescht", settings.collection)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=settings.collection,
        embedding_function=embed,
        configuration={"hnsw": {"space": "cosine"}},
        metadata={"gesetz": "SGB V", "embedding_model": settings.embedding_model},
    )

    started = time.perf_counter()
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        collection.upsert(
            ids=[c.id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[c.metadata for c in batch],
        )
        log.info("  %d/%d eingebettet", min(start + batch_size, len(chunks)), len(chunks))

    log.info(
        "fertig: %d Dokumente in %r (%.1fs, Modell %s)",
        collection.count(),
        settings.collection,
        time.perf_counter() - started,
        settings.embedding_model,
    )


# -------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rebuild", action="store_true", help="Collection vorher loeschen")
    parser.add_argument("--refresh", action="store_true", help="XML neu herunterladen statt Cache")
    parser.add_argument("--dry-run", action="store_true", help="nur parsen und chunken, nicht einbetten")
    parser.add_argument("--limit", type=int, help="nur die ersten N Chunks verarbeiten")
    parser.add_argument("--max-chars", type=int, default=3000, help="max. Zeichen je Chunk (Default: 3000)")
    parser.add_argument("--overlap", type=int, default=200, help="Ueberlappung beim Teilen (Default: 200)")
    parser.add_argument("--batch-size", type=int, default=32, help="Chunks je Embedding-Batch (Default: 32)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    settings = Settings.from_env()
    xml_path = fetch_xml(settings.raw_dir, force=args.refresh)
    chunks = build_chunks(xml_path, args.max_chars, args.overlap)

    if args.limit:
        chunks = chunks[: args.limit]
        log.info("auf %d Chunks begrenzt", len(chunks))

    if not chunks:
        log.error("keine Chunks erzeugt - Abbruch")
        return 1

    lengths = sorted(len(c.text) for c in chunks)
    log.info(
        "Chunk-Laenge min/median/max: %d/%d/%d Zeichen",
        lengths[0], lengths[len(lengths) // 2], lengths[-1],
    )

    if args.dry_run:
        for c in chunks[:3]:
            log.info("--- %s | %s", c.id, c.metadata["zitat"])
            log.info("%s ...", c.text[:300])
        log.info("dry-run: nichts geschrieben")
        return 0

    index(chunks, settings, args.batch_size, args.rebuild)
    return 0


if __name__ == "__main__":
    sys.exit(main())
