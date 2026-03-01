from __future__ import annotations
import binascii
from dataclasses import dataclass

def sum8(data: bytes) -> int:
    return sum(data) & 0xFF

def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF

@dataclass(frozen=True)
class ChecksumSpec:
    enabled: bool = False
    type: str = "none"          # none|sum8|crc16_modbus|crc32
    at: str = "append_le"       # append_le|append_be|append_u8

def apply_checksum(payload: bytes, spec: ChecksumSpec) -> bytes:
    if not spec.enabled or spec.type == "none":
        return payload
    if spec.type == "sum8":
        return payload + bytes([sum8(payload)])
    if spec.type == "crc16_modbus":
        v = crc16_modbus(payload)
        if spec.at == "append_be":
            return payload + bytes([(v >> 8) & 0xFF, v & 0xFF])
        return payload + bytes([v & 0xFF, (v >> 8) & 0xFF])
    if spec.type == "crc32":
        v = crc32(payload)
        return payload + (v.to_bytes(4, "little") if spec.at == "append_le" else v.to_bytes(4, "big"))
    raise ValueError(f"Неизвестный checksum type: {spec.type}")
