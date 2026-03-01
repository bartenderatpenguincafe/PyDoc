from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Literal
import json
from pathlib import Path
from .checksum import ChecksumSpec

ReprMode = Literal["hex", "ascii"]

@dataclass
class SerialSettings:
    port: str = ""
    baud: int = 115200
    data_bits: int = 8
    parity: str = "N"            # N/E/O/M/S
    stop_bits: float = 1.0       # 1, 1.5, 2
    flow_control: str = "none"   # none|rtscts|xonxoff
    byte_order: str = "lsb"      # lsb|msb (предпочтение)

@dataclass
class SendSequence:
    id: str
    name: str = ""
    repr: ReprMode = "hex"
    data: str = ""
    checksum: ChecksumSpec = field(default_factory=ChecksumSpec)

@dataclass
class ReceiveAction:
    type: str = "none"     # none|log|send
    text: str = ""         # supports %HEX%
    send_id: str = ""

@dataclass
class ReceiveSequence:
    id: str
    active: bool = True
    name: str = ""
    repr: ReprMode = "hex"
    pattern: str = ""      # supports ??
    action: ReceiveAction = field(default_factory=ReceiveAction)

@dataclass
class Project:
    version: int = 1
    name: str = "Untitled"
    serial: SerialSettings = field(default_factory=SerialSettings)
    send_sequences: list[SendSequence] = field(default_factory=list)
    receive_sequences: list[ReceiveSequence] = field(default_factory=list)
    documentation: str = ""
    ui_timestamps: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Project":
        p = Project()
        p.version = int(d.get("version", 1))
        p.name = str(d.get("name", "Untitled"))

        sd = d.get("serial", {}) or {}
        p.serial = SerialSettings(
            port=str(sd.get("port", "")),
            baud=int(sd.get("baud", 115200)),
            data_bits=int(sd.get("data_bits", 8)),
            parity=str(sd.get("parity", "N")),
            stop_bits=float(sd.get("stop_bits", 1.0)),
            flow_control=str(sd.get("flow_control", "none")),
            byte_order=str(sd.get("byte_order", "lsb")),
        )

        p.send_sequences = []
        for x in (d.get("send_sequences", []) or []):
            csd = (x.get("checksum", {}) or {})
            cs = ChecksumSpec(
                enabled=bool(csd.get("enabled", False)),
                type=str(csd.get("type", "none")),
                at=str(csd.get("at", "append_le")),
            )
            p.send_sequences.append(SendSequence(
                id=str(x.get("id")),
                name=str(x.get("name", "")),
                repr=str(x.get("repr", "hex")),
                data=str(x.get("data", "")),
                checksum=cs,
            ))

        p.receive_sequences = []
        for x in (d.get("receive_sequences", []) or []):
            ad = (x.get("action", {}) or {})
            act = ReceiveAction(
                type=str(ad.get("type", "none")),
                text=str(ad.get("text", "")),
                send_id=str(ad.get("send_id", "")),
            )
            p.receive_sequences.append(ReceiveSequence(
                id=str(x.get("id")),
                active=bool(x.get("active", True)),
                name=str(x.get("name", "")),
                repr=str(x.get("repr", "hex")),
                pattern=str(x.get("pattern", "")),
                action=act,
            ))

        p.documentation = str(d.get("documentation", ""))
        p.ui_timestamps = bool(d.get("ui_timestamps", True))
        return p

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "Project":
        return Project.from_dict(json.loads(path.read_text(encoding="utf-8")))
