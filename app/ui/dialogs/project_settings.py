from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox,
    QDialogButtonBox
)

from app.transports.serial_qt import SerialQt
from app.core.project import SerialSettings
from app.i18n import tr


class ProjectSettingsDialog(QDialog):
    def __init__(self, current: SerialSettings, lang: str, parent=None) -> None:
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle(tr("dlg.project_settings.title", self._lang))

        self.port = QComboBox(self)
        self.port.addItems(SerialQt.available_ports())
        if current.port:
            self.port.setCurrentText(current.port)

        self.baud = QSpinBox(self)
        self.baud.setRange(300, 3_000_000)
        self.baud.setValue(int(current.baud or 115200))

        self.data_bits = QComboBox(self)
        self.data_bits.addItems(["5", "6", "7", "8"])
        self.data_bits.setCurrentText(str(int(getattr(current, "data_bits", 8))))

        self.parity = QComboBox(self)
        self.parity.addItems([
            tr("parity.none", self._lang),
            tr("parity.even", self._lang),
            tr("parity.odd", self._lang),
            tr("parity.mark", self._lang),
            tr("parity.space", self._lang),
        ])
        par = str(getattr(current, "parity", "N")).upper()
        self.parity.setCurrentIndex({"N":0,"E":1,"O":2,"M":3,"S":4}.get(par, 0))

        self.stop_bits = QComboBox(self)
        self.stop_bits.addItems(["1", "1.5", "2"])
        sb = float(getattr(current, "stop_bits", 1.0))
        self.stop_bits.setCurrentText("1.5" if sb == 1.5 else ("2" if sb == 2.0 else "1"))

        self.flow = QComboBox(self)
        self.flow.addItems(["none", "rtscts", "xonxoff"])
        self.flow.setCurrentText(str(getattr(current, "flow_control", "none")).lower())

        self.byte_order = QComboBox(self)
        self.byte_order.addItems(["lsb", "msb"])
        self.byte_order.setCurrentText(str(getattr(current, "byte_order", "lsb")).lower())

        form = QFormLayout()
        form.addRow(tr("dlg.project_settings.port", self._lang), self.port)
        form.addRow(tr("dlg.project_settings.baud", self._lang), self.baud)
        form.addRow(tr("dlg.project_settings.data_bits", self._lang), self.data_bits)
        form.addRow(tr("dlg.project_settings.parity", self._lang), self.parity)
        form.addRow(tr("dlg.project_settings.stop_bits", self._lang), self.stop_bits)
        form.addRow(tr("dlg.project_settings.flow", self._lang), self.flow)
        form.addRow(tr("dlg.project_settings.byte_order", self._lang), self.byte_order)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def result_settings(self) -> SerialSettings:
        # parity letter from index
        par = ["N", "E", "O", "M", "S"][self.parity.currentIndex()] if 0 <= self.parity.currentIndex() <= 4 else "N"
        return SerialSettings(
            port=self.port.currentText().strip(),
            baud=int(self.baud.value()),
            data_bits=int(self.data_bits.currentText()),
            parity=par,
            stop_bits=float(self.stop_bits.currentText()),
            flow_control=self.flow.currentText(),
            byte_order=self.byte_order.currentText(),
        )
