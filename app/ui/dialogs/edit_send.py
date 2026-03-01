from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPlainTextEdit, QDialogButtonBox, QCheckBox
)

from app.core.project import SendSequence
from app.core.checksum import ChecksumSpec
from app.i18n import tr


class EditSendDialog(QDialog):
    def __init__(self, seq: SendSequence, lang: str, parent=None) -> None:
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle(tr("dlg.send.title", self._lang))

        self.name = QLineEdit(seq.name, self)

        self.repr = QComboBox(self)
        self.repr.addItems(["hex", "ascii"])
        self.repr.setCurrentText(seq.repr)

        self.data = QPlainTextEdit(self)
        self.data.setPlainText(seq.data)

        self.cs_enabled = QCheckBox(tr("dlg.send.checksum", self._lang), self)
        self.cs_enabled.setChecked(bool(seq.checksum.enabled))

        self.cs_type = QComboBox(self)
        self.cs_type.addItems(["none", "sum8", "crc16_modbus", "crc32"])
        self.cs_type.setCurrentText(seq.checksum.type)

        self.cs_at = QComboBox(self)
        self.cs_at.addItems(["append_le", "append_be", "append_u8"])
        self.cs_at.setCurrentText(seq.checksum.at)

        form = QFormLayout()
        form.addRow(tr("dlg.send.name", self._lang), self.name)
        form.addRow(tr("dlg.send.repr", self._lang), self.repr)
        form.addRow(tr("dlg.send.data", self._lang), self.data)
        form.addRow(self.cs_enabled)
        form.addRow(tr("dlg.send.cs_type", self._lang), self.cs_type)
        form.addRow(tr("dlg.send.cs_order", self._lang), self.cs_at)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def apply_to(self, seq: SendSequence) -> None:
        seq.name = self.name.text().strip()
        seq.repr = self.repr.currentText()
        seq.data = self.data.toPlainText().strip()
        seq.checksum = ChecksumSpec(
            enabled=bool(self.cs_enabled.isChecked()),
            type=self.cs_type.currentText(),
            at=self.cs_at.currentText(),
        )
