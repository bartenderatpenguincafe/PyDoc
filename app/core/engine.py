from __future__ import annotations
from datetime import datetime
from PySide6.QtCore import QObject, Signal
from .project import Project, SendSequence
from .matcher import ReceiveMatcher
from .checksum import apply_checksum
from app.util.hex_codec import parse_hex_bytes, parse_ascii_bytes, format_hex

class Engine(QObject):
    log_line = Signal(str)

    def __init__(self, transport) -> None:
        super().__init__()
        self.transport = transport
        self.project = Project()
        self.matcher = ReceiveMatcher()
        self._rx_buf = bytearray()
        self._rx_buf_max = 64 * 1024
        self.transport.rx_bytes.connect(self._on_rx)
        self.transport.error_text.connect(lambda t: self._log(f"[ERR] {t}"))
        self.transport.opened_changed.connect(lambda ok: self._log("[SYS] Connected" if ok else "[SYS] Disconnected"))

    def set_project(self, p: Project) -> None:
        self.project = p
        self.matcher.rebuild(p.receive_sequences)
        self._rx_buf.clear()

    def connect(self) -> bool:
        port = self.project.serial.port.strip()
        if not port:
            self._log("[SYS] COM порт не задан в Project Settings")
            return False
        ok = self.transport.open(self.project.serial)
        if ok:
            self._log(f"[SYS] Connected {port} @{self.project.serial.baud}")
        return ok

    def disconnect(self) -> None:
        self.transport.close()

    def send_sequence(self, s: SendSequence) -> bool:
        try:
            payload = parse_hex_bytes(s.data) if s.repr == "hex" else parse_ascii_bytes(s.data)
            payload = apply_checksum(payload, s.checksum)
        except Exception as e:
            self._log(f"[SYS] payload error '{s.name}': {e}")
            return False
        self.transport.write(payload)
        self._log(f"[TX] {s.name}: {format_hex(payload)}")
        return True

    def send_by_id(self, send_id: str) -> bool:
        s = next((x for x in self.project.send_sequences if x.id == send_id), None)
        if not s:
            self._log(f"[SYS] send id not found: {send_id}")
            return False
        return self.send_sequence(s)

    def _on_rx(self, data: bytes) -> None:
        self._rx_buf.extend(data)
        if len(self._rx_buf) > self._rx_buf_max:
            del self._rx_buf[:len(self._rx_buf) - self._rx_buf_max]

        self._log(f"[RX] {format_hex(data)}")

        matches = self.matcher.find_any(bytes(self._rx_buf), self.project.receive_sequences)
        for m in matches:
            r = next((x for x in self.project.receive_sequences if x.id == m.recv_id), None)
            if not r:
                continue
            if r.action.type == "log":
                txt = (r.action.text or "").replace("%HEX%", format_hex(m.data))
                if txt:
                    self._log(f"[ACT] {r.name}: {txt}")
            elif r.action.type == "send" and r.action.send_id:
                self._log(f"[ACT] {r.name}: auto-send '{r.action.send_id}'")
                self.send_by_id(r.action.send_id)

    def _log(self, line: str) -> None:
        if self.project.ui_timestamps:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.log_line.emit(f"{ts} {line}")
        else:
            self.log_line.emit(line)
