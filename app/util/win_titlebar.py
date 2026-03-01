from __future__ import annotations

def set_dark_titlebar(widget, enabled: bool) -> None:
    """Windows-only: enable immersive dark title bar when supported.
    Safe no-op on unsupported systems."""
    try:
        import sys
        if not sys.platform.startswith("win"):
            return
        import ctypes
        hwnd = int(widget.winId())  # ensure handle
        value = ctypes.c_int(1 if enabled else 0)
        dwm = ctypes.windll.dwmapi
        for attr in (20, 19):  # 20H1+ / earlier
            try:
                dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass
    except Exception:
        return
