from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidget

class SequenceTableWidget(QTableWidget):
    """QTableWidget with InternalMove reorder support.
    Emits orderChanged after drop.
    """
    orderChanged = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.orderChanged.emit()
