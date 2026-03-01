from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AppSettings:
    language: str = "ru"          # ru|en

    theme: str = "light"              # light|dark
    font_family: str = "Consolas"
    font_size: int = 9
    rx_color: str = "#C00000"         # RX default: red
    tx_color: str = "#0044CC"         # TX default: blue
    sys_color: str = "#444444"
    compact_ui: bool = True

def _settings_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    p = Path(base) / "PyDock"
    p.mkdir(parents=True, exist_ok=True)
    return p

def settings_path() -> Path:
    return _settings_dir() / "settings.json"

def load_settings() -> AppSettings:
    path = settings_path()
    if not path.exists():
        return AppSettings()
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        s = AppSettings()
        for k, v in d.items():
            if hasattr(s, k):
                setattr(s, k, v)
        s.theme = "dark" if str(s.theme).lower() == "dark" else "light"
        s.font_size = int(s.font_size) if int(s.font_size) > 0 else 9
        s.compact_ui = bool(s.compact_ui)
        return s
    except Exception:
        return AppSettings()

def save_settings(s: AppSettings) -> None:
    settings_path().write_text(json.dumps(asdict(s), ensure_ascii=False, indent=2), encoding="utf-8")
