from __future__ import annotations
import sys
from pathlib import Path

def app_base_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]

def resource_path(rel: str) -> Path:
    return app_base_dir() / rel
