from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent, QTextCharFormat, QColor, QTextCursor, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPlainTextEdit, QTableWidgetItem, QToolBar, QMessageBox, QFileDialog,
    QAbstractItemView, QMenu, QToolButton, QLabel, QDialog, QApplication, QHeaderView
)

from app.transports.serial_qt import SerialQt
from app.core.engine import Engine
from app.core.project import Project, SendSequence, ReceiveSequence
from app.ui.dialogs.project_settings import ProjectSettingsDialog
from app.ui.dialogs.edit_send import EditSendDialog
from app.ui.dialogs.edit_recv import EditReceiveDialog
from app.ui.dialogs.app_settings import AppSettingsDialog
from app.ui.widgets.sequence_table import SequenceTableWidget
from app.core.app_settings import AppSettings, load_settings, save_settings
from app.util.paths import resource_path
from app.i18n import tr, normalize_lang
from app.util.win_titlebar import set_dark_titlebar


class MainWindow(QMainWindow):
    LEFT_WIDTH_PX = 520

    def __init__(self) -> None:
        super().__init__()
        self._project_path: Path | None = None
        self._app_settings: AppSettings = load_settings()
        self._lang = normalize_lang(getattr(self._app_settings, "language", "ru"))

        self.transport = SerialQt()
        self.engine = Engine(self.transport)
        self.engine.log_line.connect(self._log_colored)

        self._build_ui()
        self._build_toolbar()
        self._build_statusbar()

        # заголовок окна (Win10/11 dark titlebar)
        set_dark_titlebar(self, self._app_settings.theme == "dark")

        # убираем верхние вкладки (menu bar)
        self.menuBar().hide()

        self.retranslate_ui()
        self.new_project()

    # ---------- App settings ----------
    def apply_app_settings(self, s: AppSettings) -> None:
        prev_lang = self._lang
        self._app_settings = s
        self._lang = normalize_lang(getattr(s, "language", "ru"))

        QApplication.instance().setFont(QFont(s.font_family, int(s.font_size)))  # type: ignore[call-arg]

        try:
            qss = resource_path(f"resources/themes/{s.theme}.qss").read_text(encoding="utf-8")
        except Exception:
            qss = ""

        if s.compact_ui:
            qss += "\nQToolBar { padding: 1px; }\nQHeaderView::section { padding: 2px; }\nQToolButton { padding: 1px 6px; }\n"

        QApplication.instance().setStyleSheet(qss)  # type: ignore[call-arg]
        self.comm_log.setFont(QFont(s.font_family, int(s.font_size)))
        set_dark_titlebar(self, s.theme == "dark")

        if self._lang != prev_lang:
            self.retranslate_ui()
            self._refresh_tables()

    def open_app_settings(self) -> None:
        dlg = AppSettingsDialog(self._app_settings, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            s = dlg.result_settings()
            save_settings(s)
            self.apply_app_settings(s)
            self._log_colored(tr("sys.app_settings_applied", self._lang))

    # ---------- UI helpers ----------
    @staticmethod
    def _lock_splitter(spl: QSplitter) -> None:
        spl.setChildrenCollapsible(False)
        spl.setHandleWidth(1)
        for i in range(1, spl.count()):
            h = spl.handle(i)
            if h is not None:
                h.setDisabled(True)

    @staticmethod
    def _lock_table_sizes(t: SequenceTableWidget, col_widths: list[int]) -> None:
        hh = t.horizontalHeader()
        hh.setSectionsMovable(False)
        hh.setSectionResizeMode(QHeaderView.Fixed)

        vh = t.verticalHeader()
        vh.setSectionResizeMode(QHeaderView.Fixed)
        vh.setDefaultSectionSize(18)

        for i, w in enumerate(col_widths):
            if i < t.columnCount():
                t.setColumnWidth(i, int(w))

    def retranslate_ui(self) -> None:
        self.setWindowTitle(tr("app.title", self._lang))

        # toolbar
        self.btn_file.setText(tr("toolbar.file", self._lang))
        self.act_connect.setText(tr("toolbar.connect", self._lang))
        self.act_disconnect.setText(tr("toolbar.disconnect", self._lang))
        self.act_project_settings.setText(tr("toolbar.project_settings", self._lang))
        self.act_app_settings.setText(tr("toolbar.app_settings", self._lang))

        self.act_new.setText(tr("menu.new", self._lang))
        self.act_open.setText(tr("menu.open", self._lang))
        self.act_save.setText(tr("menu.save", self._lang))
        self.act_save_as.setText(tr("menu.save_as", self._lang))

        self.lbl_sequences.setText(tr("pane.sequences", self._lang))
        self.doc.setPlaceholderText(tr("doc.placeholder", self._lang))

        self.send_table.setHorizontalHeaderLabels([
            tr("send.h0", self._lang),
            tr("send.h1", self._lang),
            tr("send.h2", self._lang),
            tr("send.h3", self._lang),
        ])
        self.recv_table.setHorizontalHeaderLabels([
            tr("recv.h0", self._lang),
            tr("recv.h1", self._lang),
            tr("recv.h2", self._lang),
            tr("recv.h3", self._lang),
        ])

        # status bar
        self._lbl_status.setText(tr("status.connected", self._lang) if self.transport.is_open() else tr("status.disconnected", self._lang))
        self._lbl_port.setText(tr("status.port", self._lang, port=(self.engine.project.serial.port or "-")))
        self._lbl_baud.setText(tr("status.baud", self._lang, baud=self.engine.project.serial.baud))

    # ---------- Build UI ----------
    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(5, 5, 5, 5)

        self.send_table = SequenceTableWidget(0, 4, self)
        self.send_table.verticalHeader().setVisible(False)
        self.send_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.send_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.send_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.send_table.customContextMenuRequested.connect(self._send_context_menu)
        self.send_table.cellDoubleClicked.connect(self._on_send_double_clicked)
        self.send_table.installEventFilter(self)
        self.send_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.recv_table = SequenceTableWidget(0, 4, self)
        self.recv_table.verticalHeader().setVisible(False)
        self.recv_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.recv_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recv_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recv_table.customContextMenuRequested.connect(self._recv_context_menu)
        self.recv_table.cellDoubleClicked.connect(self._on_recv_double_clicked)
        self.recv_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # DnD reorder (locked by default)
        self._reorder_enabled = False
        for t in (self.send_table, self.recv_table):
            t.setDragDropOverwriteMode(False)
            t.setDragEnabled(False)
            t.setAcceptDrops(False)
            t.setDropIndicatorShown(False)
            t.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.send_table.orderChanged.connect(self._sync_send_order_from_table)
        self.recv_table.orderChanged.connect(self._sync_recv_order_from_table)

        # Left wrap fixed width
        left_wrap = QWidget(self)
        left_wrap.setMinimumWidth(self.LEFT_WIDTH_PX)
        left_wrap.setMaximumWidth(self.LEFT_WIDTH_PX)

        left_lay = QVBoxLayout(left_wrap)
        left_lay.setContentsMargins(0, 0, 0, 0)

        left_hdr = QHBoxLayout()
        self.lbl_sequences = QLabel("", self)
        self.btn_reorder = QToolButton(self)
        self.btn_reorder.setText("🔒")
        self.btn_reorder.setToolTip("Перестановка строк (drag&drop)")
        self.btn_reorder.setCheckable(True)
        self.btn_reorder.toggled.connect(self._toggle_reorder)
        left_hdr.addWidget(self.lbl_sequences)
        left_hdr.addStretch(1)
        left_hdr.addWidget(self.btn_reorder)
        left_lay.addLayout(left_hdr)

        self.left_split = QSplitter(Qt.Orientation.Vertical, self)
        self.left_split.addWidget(self.send_table)
        self.left_split.addWidget(self.recv_table)
        self.left_split.setSizes([340, 340])
        left_lay.addWidget(self.left_split)

        # Right: log + doc
        self.comm_log = QTextEdit(self)
        self.comm_log.setReadOnly(True)
        self.comm_log.setAcceptRichText(False)

        self.doc = QPlainTextEdit(self)
        self.doc.setReadOnly(False)
        self.doc.textChanged.connect(self._doc_changed)

        self.right_split = QSplitter(Qt.Orientation.Vertical, self)
        self.right_split.addWidget(self.comm_log)
        self.right_split.addWidget(self.doc)
        self.right_split.setSizes([560, 200])

        self.main_split = QSplitter(Qt.Orientation.Horizontal, self)
        self.main_split.addWidget(left_wrap)
        self.main_split.addWidget(self.right_split)
        self.main_split.setSizes([self.LEFT_WIDTH_PX, 700])

        layout.addWidget(self.main_split)

        # lock splitters
        self._lock_splitter(self.left_split)
        self._lock_splitter(self.right_split)
        self._lock_splitter(self.main_split)

        # fixed columns
        self._lock_table_sizes(self.send_table, [26, 118, 54, 216])
        self._lock_table_sizes(self.recv_table, [62, 118, 150, 146])

    def _build_toolbar(self) -> None:
        tb = QToolBar("Toolbar", self)
        tb.setMovable(False)
        self.addToolBar(tb)

        self.btn_file = QToolButton(self)
        self.btn_file.setPopupMode(QToolButton.InstantPopup)

        menu_file = QMenu(self)
        self.act_new = menu_file.addAction("", self.new_project)
        self.act_open = menu_file.addAction("", self.open_project)
        menu_file.addSeparator()
        self.act_save = menu_file.addAction("", self.save_project)
        self.act_save_as = menu_file.addAction("", self.save_project_as)

        self.btn_file.setMenu(menu_file)
        tb.addWidget(self.btn_file)

        tb.addSeparator()

        self.act_connect = tb.addAction("", self._connect_clicked)
        self.act_disconnect = tb.addAction("", self.engine.disconnect)

        tb.addSeparator()

        self.act_project_settings = tb.addAction("", self.edit_project_settings)
        self.act_app_settings = tb.addAction("", self.open_app_settings)

    def _build_statusbar(self) -> None:
        self._lbl_status = QLabel("", self)
        self._lbl_port = QLabel("", self)
        self._lbl_baud = QLabel("", self)
        self.statusBar().addWidget(self._lbl_status, 1)
        self.statusBar().addPermanentWidget(self._lbl_port)
        self.statusBar().addPermanentWidget(self._lbl_baud)

    # ---------- Project ops ----------
    def new_project(self) -> None:
        p = Project(name="Без названия")
        p.send_sequences = []
        p.receive_sequences = []
        p.documentation = ""

        self._project_path = None
        self.engine.set_project(p)

        self.doc.blockSignals(True)
        self.doc.setPlainText(p.documentation)
        self.doc.blockSignals(False)

        self._refresh_tables()
        self._log_colored(tr("sys.new_project", self._lang))
        self._sync_statusbar()
        self.apply_app_settings(self._app_settings)

    def open_project(self) -> None:
        fn, _ = QFileDialog.getOpenFileName(self, tr("dlg.open", self._lang), "", "Project (*.pydock.json);;JSON (*.json)")
        if not fn:
            return
        try:
            p = Project.load(Path(fn))
        except Exception as e:
            QMessageBox.warning(self, tr("dlg.open", self._lang), f"{e}")
            return

        self._project_path = Path(fn)
        self.engine.set_project(p)

        self.doc.blockSignals(True)
        self.doc.setPlainText(p.documentation)
        self.doc.blockSignals(False)

        self._refresh_tables()
        self._log_colored(tr("sys.opened", self._lang, path=fn))
        self._sync_statusbar()

    def save_project(self) -> None:
        if not self._project_path:
            return self.save_project_as()
        self.engine.project.documentation = self.doc.toPlainText()
        try:
            self.engine.project.save(self._project_path)
            self._log_colored(tr("sys.saved", self._lang, path=str(self._project_path)))
        except Exception as e:
            QMessageBox.warning(self, tr("dlg.save", self._lang), f"{e}")

    def save_project_as(self) -> None:
        fn, _ = QFileDialog.getSaveFileName(self, tr("dlg.save", self._lang), "", "Project (*.pydock.json)")
        if not fn:
            return
        path = Path(fn)
        if not path.name.endswith(".pydock.json"):
            if path.suffix.lower() == ".json":
                path = path.with_suffix(".pydock.json")
            else:
                path = Path(str(path) + ".pydock.json")
        self._project_path = path
        self.save_project()

    # ---------- Connection ----------
    def _connect_clicked(self) -> None:
        ok = self.engine.connect()
        self._sync_statusbar()
        if not ok:
            mb = QMessageBox(self)
            mb.setIcon(QMessageBox.Information)
            mb.setWindowTitle(tr("dlg.connect", self._lang))
            mb.setText(tr("msg.connect_fail", self._lang))
            set_dark_titlebar(mb, self._app_settings.theme == "dark")
            mb.exec()

    def edit_project_settings(self) -> None:
        dlg = ProjectSettingsDialog(self.engine.project.serial, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.engine.project.serial = dlg.result_settings()
            self._sync_statusbar()

    # ---------- Sequence ops ----------
    def _send_row(self, row: int) -> None:
        if 0 <= row < len(self.engine.project.send_sequences):
            self.engine.send_sequence(self.engine.project.send_sequences[row])

    def _send_button_clicked(self) -> None:
        btn = self.sender()
        if btn is None:
            return
        row = btn.property("row")
        if isinstance(row, int):
            self._send_row(row)

    def add_send(self) -> None:
        new_id = f"s{len(self.engine.project.send_sequences)+1}"
        seq = SendSequence(id=new_id, name="", repr="hex", data="")
        dlg = EditSendDialog(seq, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply_to(seq)
            self.engine.project.send_sequences.append(seq)
            self._refresh_tables()

    def add_recv(self) -> None:
        new_id = f"r{len(self.engine.project.receive_sequences)+1}"
        seq = ReceiveSequence(id=new_id, active=True, name="", repr="hex", pattern="")
        send_ids = [s.id for s in self.engine.project.send_sequences]
        dlg = EditReceiveDialog(seq, send_ids, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply_to(seq)
            self.engine.project.receive_sequences.append(seq)
            self.engine.matcher.rebuild(self.engine.project.receive_sequences)
            self._refresh_tables()

    def edit_selected_send(self) -> None:
        row = self._selected_send_row()
        if row is None:
            return
        seq = self.engine.project.send_sequences[row]
        dlg = EditSendDialog(seq, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply_to(seq)
            self._refresh_tables()

    def edit_selected_recv(self) -> None:
        row = self._selected_recv_row()
        if row is None:
            return
        seq = self.engine.project.receive_sequences[row]
        send_ids = [s.id for s in self.engine.project.send_sequences]
        dlg = EditReceiveDialog(seq, send_ids, self._lang, self)
        set_dark_titlebar(dlg, self._app_settings.theme == "dark")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply_to(seq)
            self.engine.matcher.rebuild(self.engine.project.receive_sequences)
            self._refresh_tables()

    def del_selected_send(self) -> None:
        row = self._selected_send_row()
        if row is None:
            return
        self.engine.project.send_sequences.pop(row)
        self._refresh_tables()

    def del_selected_recv(self) -> None:
        row = self._selected_recv_row()
        if row is None:
            return
        self.engine.project.receive_sequences.pop(row)
        self.engine.matcher.rebuild(self.engine.project.receive_sequences)
        self._refresh_tables()

    # ---------- Context menus ----------
    def _send_context_menu(self, pos) -> None:
        m = QMenu(self)
        m.addAction(tr("menu.new", self._lang), self.add_send)  # reuse wording or keep
        m.addAction("Edit…", self.edit_selected_send)
        m.addAction("Delete", self.del_selected_send)
        m.exec(self.send_table.mapToGlobal(pos))

    def _recv_context_menu(self, pos) -> None:
        m = QMenu(self)
        m.addAction(tr("menu.new", self._lang), self.add_recv)
        m.addAction("Edit…", self.edit_selected_recv)
        m.addAction("Delete", self.del_selected_recv)
        m.exec(self.recv_table.mapToGlobal(pos))

    # Space to send selected row
    def eventFilter(self, obj, event):
        if obj is self.send_table and event.type() == QEvent.Type.KeyPress:
            ev: QKeyEvent = event  # type: ignore[assignment]
            if ev.key() == Qt.Key.Key_Space:
                row = self._selected_send_row()
                if row is not None:
                    self._send_row(row)
                return True
        return super().eventFilter(obj, event)

    def _on_send_double_clicked(self, row: int, _col: int) -> None:
        if row >= len(self.engine.project.send_sequences):
            self.add_send()
        else:
            self.edit_selected_send()

    def _on_recv_double_clicked(self, row: int, _col: int) -> None:
        if row >= len(self.engine.project.receive_sequences):
            self.add_recv()
        else:
            self.edit_selected_recv()

    # reorder lock
    def _toggle_reorder(self, enabled: bool) -> None:
        self._reorder_enabled = bool(enabled)
        self.btn_reorder.setText("🔓" if enabled else "🔒")
        mode = QAbstractItemView.InternalMove if enabled else QAbstractItemView.NoDragDrop
        for t in (self.send_table, self.recv_table):
            t.setDragEnabled(enabled)
            t.setAcceptDrops(enabled)
            t.setDropIndicatorShown(enabled)
            t.setDragDropMode(mode)

    def _sync_send_order_from_table(self) -> None:
        if not self._reorder_enabled:
            return
        ids: list[str] = []
        for r in range(len(self.engine.project.send_sequences)):
            it = self.send_table.item(r, 1)
            ids.append(str(it.data(Qt.ItemDataRole.UserRole) or "") if it else "")
        id2 = {s.id: s for s in self.engine.project.send_sequences}
        new_list = [id2[i] for i in ids if i in id2]
        if len(new_list) == len(self.engine.project.send_sequences):
            self.engine.project.send_sequences = new_list
            self._refresh_tables()

    def _sync_recv_order_from_table(self) -> None:
        if not self._reorder_enabled:
            return
        ids: list[str] = []
        for r in range(len(self.engine.project.receive_sequences)):
            it = self.recv_table.item(r, 1)
            ids.append(str(it.data(Qt.ItemDataRole.UserRole) or "") if it else "")
        id2 = {s.id: s for s in self.engine.project.receive_sequences}
        new_list = [id2[i] for i in ids if i in id2]
        if len(new_list) == len(self.engine.project.receive_sequences):
            self.engine.project.receive_sequences = new_list
            self.engine.matcher.rebuild(self.engine.project.receive_sequences)
            self._refresh_tables()

    # ---------- helpers ----------
    def _selected_send_row(self) -> int | None:
        row = self.send_table.currentRow()
        if row < 0 or row >= len(self.engine.project.send_sequences):
            return None
        return row

    def _selected_recv_row(self) -> int | None:
        row = self.recv_table.currentRow()
        if row < 0 or row >= len(self.engine.project.receive_sequences):
            return None
        return row

    def _refresh_tables(self) -> None:
        # SEND
        sseq = self.engine.project.send_sequences
        self.send_table.setRowCount(len(sseq) + 1)

        for i, s in enumerate(sseq):
            btn = QToolButton(self.send_table)
            btn.setText("➜")
            btn.setToolTip(tr("send.tooltip", self._lang))
            btn.setProperty("row", i)
            btn.clicked.connect(self._send_button_clicked)
            self.send_table.setCellWidget(i, 0, btn)

            it_name = QTableWidgetItem(s.name)
            it_name.setData(Qt.ItemDataRole.UserRole, s.id)
            self.send_table.setItem(i, 1, it_name)

            self.send_table.setItem(i, 2, QTableWidgetItem(s.repr))

            data_full = s.data
            data_disp = data_full if len(data_full) <= 26 else (data_full[:26] + "…")
            it_data = QTableWidgetItem(data_disp)
            it_data.setToolTip(data_full)
            self.send_table.setItem(i, 3, it_data)

        last = len(sseq)
        self.send_table.setCellWidget(last, 0, None)
        self.send_table.setItem(last, 0, QTableWidgetItem(""))
        self.send_table.setItem(last, 1, QTableWidgetItem(tr("send.add_hint", self._lang)))
        self.send_table.setItem(last, 2, QTableWidgetItem(""))
        self.send_table.setItem(last, 3, QTableWidgetItem(""))

        # RECV
        rseq = self.engine.project.receive_sequences
        self.recv_table.setRowCount(len(rseq) + 1)

        for i, r in enumerate(rseq):
            it_on = QTableWidgetItem("✓" if r.active else "")
            it_on.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recv_table.setItem(i, 0, it_on)

            it_name = QTableWidgetItem(r.name)
            it_name.setData(Qt.ItemDataRole.UserRole, r.id)
            self.recv_table.setItem(i, 1, it_name)

            self.recv_table.setItem(i, 2, QTableWidgetItem(r.pattern))

            act = r.action.type
            if act == "log":
                act_full = f"comment: {r.action.text}" if self._lang == "en" else f"коммент: {r.action.text}"
            elif act == "send":
                act_full = f"reply: {r.action.send_id}" if self._lang == "en" else f"ответ: {r.action.send_id}"
            else:
                act_full = act

            act_disp = act_full if len(act_full) <= 22 else (act_full[:22] + "…")
            it_act = QTableWidgetItem(act_disp)
            it_act.setToolTip(act_full)
            self.recv_table.setItem(i, 3, it_act)

        last2 = len(rseq)
        self.recv_table.setItem(last2, 0, QTableWidgetItem(""))
        self.recv_table.setItem(last2, 1, QTableWidgetItem(tr("send.add_hint", self._lang)))
        self.recv_table.setItem(last2, 2, QTableWidgetItem(""))
        self.recv_table.setItem(last2, 3, QTableWidgetItem(""))

        # fixed widths
        self._lock_table_sizes(self.send_table, [26, 118, 54, 216])
        self._lock_table_sizes(self.recv_table, [62, 118, 150, 146])

    def _log_colored(self, line: str) -> None:
        s = self._app_settings
        color = s.sys_color
        if "[RX]" in line:
            color = s.rx_color
        elif "[TX]" in line:
            color = s.tx_color
        elif "[ERR]" in line:
            color = s.rx_color

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur = self.comm_log.textCursor()
        cur.movePosition(QTextCursor.End)
        cur.insertText(line + "\n", fmt)
        self.comm_log.setTextCursor(cur)
        self.comm_log.ensureCursorVisible()

    def _doc_changed(self) -> None:
        self.engine.project.documentation = self.doc.toPlainText()

    def _sync_statusbar(self) -> None:
        self._lbl_status.setText(tr("status.connected", self._lang) if self.transport.is_open() else tr("status.disconnected", self._lang))
        self._lbl_port.setText(tr("status.port", self._lang, port=(self.engine.project.serial.port or "-")))
        self._lbl_baud.setText(tr("status.baud", self._lang, baud=self.engine.project.serial.baud))
