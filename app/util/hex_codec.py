from __future__ import annotations
import re

_HEX_TOKEN = re.compile(r"^[0-9A-Fa-f]{2}$")

def parse_hex_bytes(s: str) -> bytes:
    s = s.strip()
    if not s:
        return b""
    if " " not in s and len(s) % 2 == 0:
        return bytes.fromhex(s)
    parts = [p for p in s.replace("\t", " ").split(" ") if p]
    for p in parts:
        if not _HEX_TOKEN.match(p):
            raise ValueError(f"Некорректный HEX-токен: '{p}'")
    return bytes(int(p, 16) for p in parts)

def format_hex(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)

def parse_ascii_bytes(s: str) -> bytes:
    return s.encode("latin-1", errors="replace")
