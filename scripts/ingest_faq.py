#!/usr/bin/env python3
"""Indexiert die handgeschriebene FAQ-Ebene in dieselbe Chroma-Collection.

Der Normtext des SGB V beantwortet Fragen in Gesetzessprache. Nutzerinnen
fragen in Alltagssprache. Diese Ebene schliesst die Luecke: jeder Eintrag
buendelt mehrere Alltagsformulierungen mit einer kurzen Antwort und zeigt
auf die Fundstelle im Gesetz.

    uv run scripts/ingest_faq.py
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import yaml

from health_faq_agent.config import PROJECT_ROOT, Settings

FAQ_PATH = PROJECT_ROOT / "data" / "faq" / "faq.yaml"
NORM_URL = "https://www.gesetze-im-internet.de/sgb_5/__{num}.html"
PARA_NR_RE = re.compile(r"§+\s*(\d+[a-z]?)")

log = logging.getLogger("ingest-faq")


def build_documents(entries: list[dict]) -> tuple[list[str], list[str], list[dict]]:
    ids, docs, metas = [], [], []

    for entry in entries:
        frage = entry["frage"].strip()
        varianten = [v.strip() for v in entry.get("varianten", [])]
        antwort = " ".join(entry["antwort"].split())
        zitate = entry.get("zitate", [])

        # Alle Formulierungen in EIN Dokument: der Vektor liegt damit in der
        # Mitte der Paraphrasen und trifft ein breiteres Spektrum an Fragen,
        # ohne die Trefferliste mit Dubletten desselben Eintrags zu fluten.
        text = "\n".join(
            [
                f"Frage: {frage}",
                f"Aehnliche Fragen: {' | '.join(varianten)}" if varianten else "",
                f"Antwort: {antwort}",
                f"Rechtsgrundlage: {', '.join(zitate)}" if zitate else "",
            ]
        )

        nummern = [m.group(1) for z in zitate for m in [PARA_NR_RE.search(z)] if m]

        ids.append(entry["id"])
        docs.append("\n".join(line for line in text.split("\n") if line))
        metas.append(
            {
                "typ": "faq",
                "gesetz": "SGB V",
                "zitat": ", ".join(zitate),
                "paragraph_nr": ",".join(nummern),
                "source_url": NORM_URL.format(num=nummern[0]) if nummern else "",
                "n_varianten": len(varianten),
            }
        )

    return ids, docs, metas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--faq-path", type=Path, default=FAQ_PATH)
    parser.add_argument("--purge", action="store_true", help="bestehende FAQ-Chunks vorher entfernen")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")

    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

    settings = Settings.from_env()
    entries = yaml.safe_load(args.faq_path.read_text(encoding="utf-8"))
    log.info("%d FAQ-Eintraege aus %s", len(entries), args.faq_path.name)

    ids, docs, metas = build_documents(entries)

    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    collection = client.get_or_create_collection(
        name=settings.collection,
        embedding_function=OllamaEmbeddingFunction(
            url=settings.ollama_host, model_name=settings.embedding_model
        ),
        configuration={"hnsw": {"space": "cosine"}},
    )

    if args.purge:
        existing = collection.get(where={"typ": "faq"})["ids"]
        if existing:
            collection.delete(ids=existing)
            log.info("%d alte FAQ-Chunks entfernt", len(existing))

    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    log.info(
        "fertig: %d FAQ-Chunks indexiert, Collection %r enthaelt jetzt %d Dokumente",
        len(ids), settings.collection, collection.count(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
