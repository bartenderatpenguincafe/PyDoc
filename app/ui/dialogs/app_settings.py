from __future__ import annotations

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox,
    QPushButton, QColorDialog, QCheckBox
)
from PySide6.QtWidgets import QFontComboBox

from app.core.app_settings import AppSettings
from app.i18n import tr


class AppSettingsDialog(QDialog):
    def __init__(self, current: AppSettings, lang: str, parent=None) -> None:
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle(tr("dlg.app_settings.title", self._lang))

        self.language = QComboBox(self)
        self.language.addItem(tr("lang.ru", self._lang), "ru")
        self.language.addItem(tr("lang.en", self._lang), "en")
        # set current
        idx = 0 if (getattr(current, "language", "ru") == "ru") else 1
        self.language.setCurrentIndex(idx)

        self.theme = QComboBox(self)
        self.theme.addItems(["light", "dark"])
        self.theme.setCurrentText(current.theme)

        self.font_family = QFontComboBox(self)
        self.font_family.setCurrentFont(QFont(current.font_family))

        self.font_size = QSpinBox(self)
        self.font_size.setRange(6, 24)
        self.font_size.setValue(int(current.font_size))

        self.compact = QCheckBox(tr("dlg.app_settings.compact", self._lang), self)
        self.compact.setChecked(bool(current.compact_ui))

        self.rx_btn = QPushButton(current.rx_color, self)
        self.tx_btn = QPushButton(current.tx_color, self)
        self.sys_btn = QPushButton(current.sys_color, self)

        self.rx_btn.clicked.connect(lambda: self._pick_color(self.rx_btn))
        self.tx_btn.clicked.connect(lambda: self._pick_color(self.tx_btn))
        self.sys_btn.clicked.connect(lambda: self._pick_color(self.sys_btn))

        form = QFormLayout()
        form.addRow(tr("dlg.app_settings.lang", self._lang), self.language)
        form.addRow(tr("dlg.app_settings.theme", self._lang), self.theme)
        form.addRow(tr("dlg.app_settings.font", self._lang), self.font_family)
        form.addRow(tr("dlg.app_settings.font_size", self._lang), self.font_size)
        form.addRow(self.compact)
        form.addRow(tr("dlg.app_settings.rx", self._lang), self.rx_btn)
        form.addRow(tr("dlg.app_settings.tx", self._lang), self.tx_btn)
        form.addRow(tr("dlg.app_settings.sys", self._lang), self.sys_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def _pick_color(self, btn: QPushButton) -> None:
        col = QColorDialog.getColor(QColor(btn.text()), self, tr("color.pick", self._lang))
        if col.isValid():
            btn.setText(col.name())

    def result_settings(self) -> AppSettings:
        lang_code = self.language.currentData()
        if lang_code not in ("ru", "en"):
            lang_code = "ru"
        return AppSettings(
            language=lang_code,
            theme=self.theme.currentText(),
            font_family=self.font_family.currentFont().family(),
            font_size=int(self.font_size.value()),
            rx_color=self.rx_btn.text(),
            tx_color=self.tx_btn.text(),
            sys_color=self.sys_btn.text(),
            compact_ui=bool(self.compact.isChecked()),
        )
