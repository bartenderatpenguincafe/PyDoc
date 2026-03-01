from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QCheckBox
)

from app.core.project import ReceiveSequence, ReceiveAction
from app.i18n import tr


class EditReceiveDialog(QDialog):
    def __init__(self, seq: ReceiveSequence, send_ids: list[str], lang: str, parent=None) -> None:
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle(tr("dlg.recv.title", self._lang))

        self.active = QCheckBox(tr("dlg.recv.active", self._lang), self)
        self.active.setChecked(bool(seq.active))

        self.name = QLineEdit(seq.name, self)
        self.pattern = QLineEdit(seq.pattern, self)

        self.action_type = QComboBox(self)
        self.action_type.addItems(["none", "log", "send"])
        self.action_type.setCurrentText(seq.action.type)

        self.action_text = QLineEdit(seq.action.text, self)

        self.action_send_id = QComboBox(self)
        self.action_send_id.addItems([""] + send_ids)
        if seq.action.send_id:
            self.action_send_id.setCurrentText(seq.action.send_id)

        form = QFormLayout()
        form.addRow(self.active)
        form.addRow(tr("dlg.recv.name", self._lang), self.name)
        form.addRow(tr("dlg.recv.pattern", self._lang), self.pattern)
        form.addRow(tr("dlg.recv.action", self._lang), self.action_type)
        form.addRow(tr("dlg.recv.text", self._lang), self.action_text)
        form.addRow(tr("dlg.recv.autosend", self._lang), self.action_send_id)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def apply_to(self, seq: ReceiveSequence) -> None:
        seq.active = bool(self.active.isChecked())
        seq.name = self.name.text().strip()
        seq.repr = "hex"
        seq.pattern = self.pattern.text().strip()
        seq.action = ReceiveAction(
            type=self.action_type.currentText(),
            text=self.action_text.text().strip(),
            send_id=self.action_send_id.currentText().strip(),
        )
