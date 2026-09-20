#!/usr/bin/env python3
"""Measure retrieval quality against the golden set.

Retrieval only, no LLM: answers the question of whether the correct
provision even makes it into the context. Runs in seconds, which makes it
the fast feedback loop when tuning chunking, model and k.

    uv run scripts/eval_retrieval.py
    uv run scripts/eval_retrieval.py --no-faq   # baseline without FAQ layer
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from health_faq_agent.config import PROJECT_ROOT, Settings

GOLDEN = PROJECT_ROOT / "data" / "eval" / "golden_set.yaml"


def recall_at(hit_rank: int | None, k: int) -> bool:
    return hit_rank is not None and hit_rank <= k


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=GOLDEN)
    parser.add_argument("--k", type=int, default=10, help="how many results to fetch")
    parser.add_argument("--no-faq", action="store_true", help="hide the FAQ layer (baseline)")
    parser.add_argument("--details", action="store_true", help="print every question")
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

    questions = [
        e for e in yaml.safe_load(args.golden.read_text(encoding="utf-8")) if e["type"] == "answerable"
    ]
    where = {"type": {"$ne": "faq"}} if args.no_faq else None

    ranks: list[int | None] = []
    for entry in questions:
        res = collection.query(query_texts=[entry["question"]], n_results=args.k, where=where)
        expected = set(entry["expected_paragraphs"])

        rank = None
        for i, meta in enumerate(res["metadatas"][0], 1):
            # FAQ chunks may cite several paragraphs
            cited = set(str(meta.get("paragraph_nr", "")).split(","))
            if cited & expected:
                rank = i
                break
        ranks.append(rank)

        if args.details:
            status = f"rank {rank}" if rank else "not found"
            print(f"  [{status:>12}] {entry['id']}  {entry['question'][:62]}")

    n = len(questions)
    label = "without FAQ layer (baseline)" if args.no_faq else "with FAQ layer"
    print(f"\n{label} - {n} answerable questions, k={args.k}")
    for k in (1, 3, 5, 10):
        if k > args.k:
            continue
        hits = sum(recall_at(r, k) for r in ranks)
        print(f"  Recall@{k:<3} {hits:>2}/{n}  ({hits / n:.0%})")

    found = [r for r in ranks if r]
    if found:
        print(f"  mean rank of hits: {sum(found) / len(found):.1f}")
    missed = [q["id"] for q, r in zip(questions, ranks) if r is None]
    if missed:
        print(f"  outside k={args.k}: {', '.join(missed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
