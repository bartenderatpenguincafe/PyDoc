from __future__ import annotations
import re
from dataclasses import dataclass
from .project import ReceiveSequence

@dataclass
class MatchResult:
    recv_id: str
    start: int
    end: int
    data: bytes

def compile_hex_pattern(pattern: str) -> re.Pattern[bytes]:
    parts = [p for p in pattern.replace("\t", " ").split(" ") if p]
    if not parts:
        return re.compile(b"(?!x)x")
    chunks: list[bytes] = []
    for tok in parts:
        if tok == "??":
            chunks.append(b".")
        else:
            chunks.append(bytes([int(tok, 16)]))
    regex = b"".join((c if c == b"." else re.escape(c)) for c in chunks)
    return re.compile(regex, flags=re.DOTALL)

class ReceiveMatcher:
    def __init__(self) -> None:
        self._compiled: dict[str, re.Pattern[bytes]] = {}

    def rebuild(self, receives: list[ReceiveSequence]) -> None:
        self._compiled.clear()
        for r in receives:
            if r.repr != "hex":
                continue
            try:
                self._compiled[r.id] = compile_hex_pattern(r.pattern)
            except Exception:
                pass

    def find_any(self, buf: bytes, receives: list[ReceiveSequence]) -> list[MatchResult]:
        out: list[MatchResult] = []
        for r in receives:
            if not r.active:
                continue
            pat = self._compiled.get(r.id)
            if not pat:
                continue
            m = pat.search(buf)
            if m:
                out.append(MatchResult(r.id, m.start(), m.end(), buf[m.start():m.end()]))
        return out
