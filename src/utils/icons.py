"""Gestion de iconos de la aplicacion."""

import os
import sys
from pathlib import Path
from typing import Optional

import tkinter as tk
from PIL import Image


def get_resource_path(relative_path: str) -> Path:
    """Obtiene la ruta absoluta del recurso."""
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path


def load_window_icon(window: tk.Tk, icon_path: Optional[str] = None) -> None:
    """Carga el icono de la ventana y barra de tareas."""
    if icon_path is None:
        icon_path = get_resource_path("assets/icon.ico")
    else:
        icon_path = Path(icon_path)
    
    if not icon_path.exists():
        return
    
    try:
        window.iconbitmap(str(icon_path))
    except Exception:
        pass


def set_taskbar_icon(window: tk.Tk, icon_path: Optional[str] = None) -> None:
    """Establece el icono de la barra de tareas (Windows)."""
    if icon_path is None:
        icon_path = get_resource_path("assets/icon.ico")
    else:
        icon_path = Path(icon_path)
    
    if not icon_path.exists():
        return
    
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PycResizer")
        window.iconbitmap(str(icon_path))
    except Exception:
        pass
