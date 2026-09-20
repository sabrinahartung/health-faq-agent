"""Zentrale Konfiguration, ausschliesslich ueber Environment-Variablen.

Alle Werte haben Defaults, die lokal ohne .env funktionieren. Im Container
werden sie ueber `environment:` in der Compose-Datei gesetzt.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path(env: str, default: Path) -> Path:
    raw = os.getenv(env)
    return Path(raw).expanduser() if raw else default


@dataclass(frozen=True)
class Settings:
    ollama_host: str
    embedding_model: str
    chat_model: str
    chroma_path: Path
    collection: str
    raw_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "bge-m3"),
            chat_model=os.getenv("CHAT_MODEL", "llama3.2:3b"),
            chroma_path=_path("CHROMA_PATH", PROJECT_ROOT / "data" / "chroma"),
            collection=os.getenv("CHROMA_COLLECTION", "sgb5"),
            raw_dir=_path("DATA_RAW_DIR", PROJECT_ROOT / "data" / "raw"),
        )
