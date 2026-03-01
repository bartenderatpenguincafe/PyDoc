from __future__ import annotations

from typing import Mapping

_LANGS = ("ru", "en")

_TR: dict[str, dict[str, str]] = {
    "ru": {
        # main
        "app.title": "PyDock — COM терминал",
        "toolbar.file": "Файл",
        "toolbar.connect": "Подключиться",
        "toolbar.disconnect": "Отключиться",
        "toolbar.project_settings": "Настройки проекта",
        "toolbar.app_settings": "Настройки приложения",
        "menu.new": "Новый",
        "menu.open": "Открыть…",
        "menu.save": "Сохранить",
        "menu.save_as": "Сохранить как…",
        "pane.sequences": "Последовательности",
        "send.tooltip": "Отправить",
        "send.add_hint": "<двойной клик: добавить>",
        "doc.placeholder": "Заметки по проекту...",
        "status.disconnected": "Не подключено",
        "status.connected": "Подключено",
        "status.port": "Порт: {port}",
        "status.baud": "Baud: {baud}",
        # tables
        "send.h0": "",
        "send.h1": "Имя",
        "send.h2": "Формат",
        "send.h3": "Последовательность",
        "recv.h0": "Активно",
        "recv.h1": "Имя",
        "recv.h2": "Шаблон",
        "recv.h3": "Действие",
        # sys logs
        "sys.new_project": "[SYS] Новый проект",
        "sys.opened": "[SYS] Открыт: {path}",
        "sys.saved": "[SYS] Сохранено: {path}",
        "sys.app_settings_applied": "[SYS] Настройки приложения применены",
        "msg.connect_fail": "Не удалось подключиться. Проверьте COM-порт в настройках проекта.",
        "dlg.connect": "Подключение",
        "dlg.open": "Открыть",
        "dlg.save": "Сохранить",
        # dialogs common
        "ok": "OK",
        "cancel": "Cancel",
        # project settings dialog
        "dlg.project_settings.title": "Настройки проекта (COM)",
        "dlg.project_settings.port": "COM-порт:",
        "dlg.project_settings.baud": "Скорость (baud):",
        "dlg.project_settings.data_bits": "Биты данных:",
        "dlg.project_settings.parity": "Чётность:",
        "dlg.project_settings.stop_bits": "Стоп-биты:",
        "dlg.project_settings.flow": "Контроль потока:",
        "dlg.project_settings.byte_order": "Порядок байт (LSB/MSB):",
        "parity.none": "N (нет)",
        "parity.even": "E (even)",
        "parity.odd": "O (odd)",
        "parity.mark": "M (mark)",
        "parity.space": "S (space)",
        # app settings dialog
        "dlg.app_settings.title": "Настройки приложения",
        "dlg.app_settings.lang": "Язык:",
        "dlg.app_settings.theme": "Тема:",
        "dlg.app_settings.font": "Шрифт:",
        "dlg.app_settings.font_size": "Размер шрифта:",
        "dlg.app_settings.compact": "Компактный интерфейс",
        "dlg.app_settings.rx": "Цвет RX (принято):",
        "dlg.app_settings.tx": "Цвет TX (отправлено):",
        "dlg.app_settings.sys": "Цвет SYS/прочее:",
        "color.pick": "Выбор цвета",
        "lang.ru": "Русский",
        "lang.en": "English",
        # edit send
        "dlg.send.title": "Отправка: редактирование",
        "dlg.send.name": "Имя:",
        "dlg.send.repr": "Формат:",
        "dlg.send.data": "Данные:",
        "dlg.send.checksum": "Контрольная сумма",
        "dlg.send.cs_type": "Тип КС:",
        "dlg.send.cs_order": "Порядок байт:",
        # edit recv
        "dlg.recv.title": "Приём: редактирование",
        "dlg.recv.active": "Активно",
        "dlg.recv.name": "Имя:",
        "dlg.recv.pattern": "Шаблон (HEX, допускается \"??\"):",
        "dlg.recv.action": "Действие:",
        "dlg.recv.text": "Текст (макрос %HEX%):",
        "dlg.recv.autosend": "Авто-ответ (ID отправки):",
    },
    "en": {
        # main
        "app.title": "PyDock — COM terminal",
        "toolbar.file": "File",
        "toolbar.connect": "Connect",
        "toolbar.disconnect": "Disconnect",
        "toolbar.project_settings": "Project settings",
        "toolbar.app_settings": "App settings",
        "menu.new": "New",
        "menu.open": "Open…",
        "menu.save": "Save",
        "menu.save_as": "Save as…",
        "pane.sequences": "Sequences",
        "send.tooltip": "Send",
        "send.add_hint": "<double click: add>",
        "doc.placeholder": "Project notes...",
        "status.disconnected": "Disconnected",
        "status.connected": "Connected",
        "status.port": "Port: {port}",
        "status.baud": "Baud: {baud}",
        # tables
        "send.h0": "",
        "send.h1": "Name",
        "send.h2": "Format",
        "send.h3": "Sequence",
        "recv.h0": "Active",
        "recv.h1": "Name",
        "recv.h2": "Pattern",
        "recv.h3": "Action",
        # sys logs
        "sys.new_project": "[SYS] New project",
        "sys.opened": "[SYS] Opened: {path}",
        "sys.saved": "[SYS] Saved: {path}",
        "sys.app_settings_applied": "[SYS] App settings applied",
        "msg.connect_fail": "Failed to connect. Check COM port in project settings.",
        "dlg.connect": "Connection",
        "dlg.open": "Open",
        "dlg.save": "Save",
        # dialogs common
        "ok": "OK",
        "cancel": "Cancel",
        # project settings dialog
        "dlg.project_settings.title": "Project settings (COM)",
        "dlg.project_settings.port": "COM port:",
        "dlg.project_settings.baud": "Baud rate:",
        "dlg.project_settings.data_bits": "Data bits:",
        "dlg.project_settings.parity": "Parity:",
        "dlg.project_settings.stop_bits": "Stop bits:",
        "dlg.project_settings.flow": "Flow control:",
        "dlg.project_settings.byte_order": "Byte order (LSB/MSB):",
        "parity.none": "N (none)",
        "parity.even": "E (even)",
        "parity.odd": "O (odd)",
        "parity.mark": "M (mark)",
        "parity.space": "S (space)",
        # app settings dialog
        "dlg.app_settings.title": "Application settings",
        "dlg.app_settings.lang": "Language:",
        "dlg.app_settings.theme": "Theme:",
        "dlg.app_settings.font": "Font:",
        "dlg.app_settings.font_size": "Font size:",
        "dlg.app_settings.compact": "Compact UI",
        "dlg.app_settings.rx": "RX color (received):",
        "dlg.app_settings.tx": "TX color (sent):",
        "dlg.app_settings.sys": "SYS/other color:",
        "color.pick": "Pick a color",
        "lang.ru": "Русский",
        "lang.en": "English",
        # edit send
        "dlg.send.title": "Send: edit",
        "dlg.send.name": "Name:",
        "dlg.send.repr": "Format:",
        "dlg.send.data": "Data:",
        "dlg.send.checksum": "Checksum",
        "dlg.send.cs_type": "Checksum type:",
        "dlg.send.cs_order": "Byte order:",
        # edit recv
        "dlg.recv.title": "Receive: edit",
        "dlg.recv.active": "Active",
        "dlg.recv.name": "Name:",
        "dlg.recv.pattern": "Pattern (HEX, \"??\" allowed):",
        "dlg.recv.action": "Action:",
        "dlg.recv.text": "Text (%HEX% macro):",
        "dlg.recv.autosend": "Auto reply (Send ID):",
    }
}

def normalize_lang(lang: str | None) -> str:
    if not lang:
        return "ru"
    lang = str(lang).lower().strip()
    return lang if lang in _LANGS else "ru"

def tr(key: str, lang: str = "ru", **fmt) -> str:
    lang = normalize_lang(lang)
    s = _TR.get(lang, {}).get(key)
    if s is None:
        # fallback: ru then key
        s = _TR.get("ru", {}).get(key, key)
    if fmt:
        try:
            return s.format(**fmt)
        except Exception:
            return s
    return s
