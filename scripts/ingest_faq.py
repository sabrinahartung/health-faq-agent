#!/usr/bin/env python3
"""Index the hand-written FAQ layer into the same Chroma collection.

The statutory text of SGB V answers questions in legal German. Users ask in
everyday German. This layer bridges the gap: each entry bundles several
colloquial phrasings with a short answer and points at the provision.

Note: the indexed text stays German on purpose. It exists to match German
user queries - translating it would break the thing it was built for.

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
        question = entry["question"].strip()
        variants = [v.strip() for v in entry.get("variants", [])]
        answer = " ".join(entry["answer"].split())
        citations = entry.get("citations", [])

        # All phrasings go into ONE document: the vector then sits in the
        # middle of the paraphrases and covers a wider range of questions
        # without flooding the result list with duplicates of one entry.
        text = "\n".join(
            [
                f"Frage: {question}",
                f"Aehnliche Fragen: {' | '.join(variants)}" if variants else "",
                f"Antwort: {answer}",
                f"Rechtsgrundlage: {', '.join(citations)}" if citations else "",
            ]
        )

        numbers = [m.group(1) for c in citations for m in [PARA_NR_RE.search(c)] if m]

        ids.append(entry["id"])
        docs.append("\n".join(line for line in text.split("\n") if line))
        metas.append(
            {
                "type": "faq",
                "law": "SGB V",
                "citation": ", ".join(citations),
                "paragraph_nr": ",".join(numbers),
                "source_url": NORM_URL.format(num=numbers[0]) if numbers else "",
                "n_variants": len(variants),
            }
        )

    return ids, docs, metas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--faq-path", type=Path, default=FAQ_PATH)
    parser.add_argument("--purge", action="store_true", help="remove existing FAQ chunks first")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")

    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

    settings = Settings.from_env()
    entries = yaml.safe_load(args.faq_path.read_text(encoding="utf-8"))
    log.info("%d FAQ entries from %s", len(entries), args.faq_path.name)

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
        existing = collection.get(where={"type": "faq"})["ids"]
        if existing:
            collection.delete(ids=existing)
            log.info("removed %d stale FAQ chunks", len(existing))

    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    log.info(
        "done: %d FAQ chunks indexed, collection %r now holds %d documents",
        len(ids), settings.collection, collection.count(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
