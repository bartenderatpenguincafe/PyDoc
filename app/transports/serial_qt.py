from __future__ import annotations
from PySide6.QtCore import QObject, Signal
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from app.core.project import SerialSettings

class SerialQt(QObject):
    rx_bytes = Signal(bytes)
    error_text = Signal(str)
    opened_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._sp = QSerialPort(self)
        self._sp.readyRead.connect(self._on_ready_read)
        self._sp.errorOccurred.connect(self._on_error)

    @staticmethod
    def available_ports() -> list[str]:
        return [p.portName() for p in QSerialPortInfo.availablePorts()]

    def is_open(self) -> bool:
        return self._sp.isOpen()

    def open(self, s: SerialSettings) -> bool:
        if self._sp.isOpen():
            self._sp.close()

        self._sp.setPortName(s.port)
        self._sp.setBaudRate(int(s.baud))

        db_map = {5: QSerialPort.Data5, 6: QSerialPort.Data6, 7: QSerialPort.Data7, 8: QSerialPort.Data8}
        self._sp.setDataBits(db_map.get(int(s.data_bits), QSerialPort.Data8))

        par_map = {"N": QSerialPort.NoParity, "E": QSerialPort.EvenParity, "O": QSerialPort.OddParity,
                   "M": QSerialPort.MarkParity, "S": QSerialPort.SpaceParity}
        self._sp.setParity(par_map.get(str(s.parity).upper(), QSerialPort.NoParity))

        sb = float(s.stop_bits)
        if sb == 2.0:
            self._sp.setStopBits(QSerialPort.TwoStop)
        elif sb == 1.5:
            self._sp.setStopBits(QSerialPort.OneAndHalfStop)
        else:
            self._sp.setStopBits(QSerialPort.OneStop)

        fc = str(s.flow_control).lower()
        if fc == "rtscts":
            self._sp.setFlowControl(QSerialPort.HardwareControl)
        elif fc == "xonxoff":
            self._sp.setFlowControl(QSerialPort.SoftwareControl)
        else:
            self._sp.setFlowControl(QSerialPort.NoFlowControl)

        ok = self._sp.open(QSerialPort.ReadWrite)
        self.opened_changed.emit(ok)
        if not ok:
            self.error_text.emit(f"Не открылся порт {s.port}")
        return ok

    def close(self) -> None:
        if self._sp.isOpen():
            self._sp.close()
        self.opened_changed.emit(False)

    def write(self, data: bytes) -> None:
        if not self._sp.isOpen():
            self.error_text.emit("Порт не открыт")
            return
        self._sp.write(data)

    def _on_ready_read(self) -> None:
        data = bytes(self._sp.readAll())
        if data:
            self.rx_bytes.emit(data)

    def _on_error(self, _err) -> None:
        if self._sp.error() != QSerialPort.NoError:
            self.error_text.emit(self._sp.errorString())
