#!/usr/bin/env python3
"""Misst die Retrieval-Qualitaet gegen das Golden Set.

Nur Retrieval, kein LLM: beantwortet die Frage, ob der richtige Paragraph
ueberhaupt in den Kontext gelangt. Laeuft in Sekunden und ist damit die
schnelle Rueckkopplung beim Tunen von Chunking, Modell und k.

    uv run scripts/eval_retrieval.py
    uv run scripts/eval_retrieval.py --ohne-faq   # Baseline ohne FAQ-Ebene
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from health_faq_agent.config import PROJECT_ROOT, Settings

GOLDEN = PROJECT_ROOT / "data" / "eval" / "golden_set.yaml"


def recall_at(treffer_rang: int | None, k: int) -> bool:
    return treffer_rang is not None and treffer_rang <= k


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=GOLDEN)
    parser.add_argument("--k", type=int, default=10, help="wie viele Treffer geholt werden")
    parser.add_argument("--ohne-faq", action="store_true", help="FAQ-Ebene ausblenden (Baseline)")
    parser.add_argument("--details", action="store_true", help="jede Frage einzeln ausgeben")
    args = parser.parse_args(argv)

    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

    settings = Settings.from_env()
    collection = chromadb.PersistentClient(path=str(settings.chroma_path)).get_collection(
        settings.collection,
        embedding_function=OllamaEmbeddingFunction(
            url=settings.ollama_host, model_name=settings.embedding_model
        ),
    )

    fragen = [e for e in yaml.safe_load(args.golden.read_text(encoding="utf-8")) if e["typ"] == "beantwortbar"]
    where = {"typ": {"$ne": "faq"}} if args.ohne_faq else None

    raenge: list[int | None] = []
    for eintrag in fragen:
        res = collection.query(query_texts=[eintrag["frage"]], n_results=args.k, where=where)
        erwartet = set(eintrag["erwartete_paragraphen"])

        rang = None
        for i, meta in enumerate(res["metadatas"][0], 1):
            # FAQ-Chunks koennen mehrere Paragraphen nennen
            genannt = set(str(meta.get("paragraph_nr", "")).split(","))
            if genannt & erwartet:
                rang = i
                break
        raenge.append(rang)

        if args.details:
            status = f"Rang {rang}" if rang else "nicht gefunden"
            print(f"  [{status:>14}] {eintrag['id']}  {eintrag['frage'][:62]}")

    n = len(fragen)
    label = "ohne FAQ-Ebene (Baseline)" if args.ohne_faq else "mit FAQ-Ebene"
    print(f"\n{label} - {n} beantwortbare Fragen, k={args.k}")
    for k in (1, 3, 5, 10):
        if k > args.k:
            continue
        treffer = sum(recall_at(r, k) for r in raenge)
        print(f"  Recall@{k:<3} {treffer:>2}/{n}  ({treffer / n:.0%})")

    gefunden = [r for r in raenge if r]
    if gefunden:
        print(f"  mittlerer Rang der Treffer: {sum(gefunden) / len(gefunden):.1f}")
    verfehlt = [f["id"] for f, r in zip(fragen, raenge) if r is None]
    if verfehlt:
        print(f"  ausserhalb k={args.k}: {', '.join(verfehlt)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
