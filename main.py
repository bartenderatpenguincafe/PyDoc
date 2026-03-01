import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from app.ui.main_window import MainWindow
from app.util.paths import resource_path
from app.core.app_settings import load_settings

def _apply_theme(app: QApplication, theme: str, compact: bool) -> None:
    qss_path = resource_path(f"resources/themes/{theme}.qss")
    try:
        qss = qss_path.read_text(encoding="utf-8")
    except Exception:
        qss = ""
    if compact:
        qss += "\nQToolBar { padding: 1px; }\nQHeaderView::section { padding: 2px; }\nQToolButton { padding: 1px 4px; }\n"
    app.setStyleSheet(qss)

def main() -> int:
    app = QApplication(sys.argv)
    s = load_settings()
    app.setFont(QFont(s.font_family, int(s.font_size)))
    _apply_theme(app, s.theme, bool(s.compact_ui))
    w = MainWindow()
    w.apply_app_settings(s)
    w.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
