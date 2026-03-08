"""Componentes reutilizables de la GUI."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import List, Optional

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..utils import SUPPORTED_EXTENSIONS
from ..utils.i18n import tr
from .settings_window import SettingsWindow

try:
    from ttkbootstrap_icons_bs import BootstrapIcon
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False


def _get_icon(name: str, size: int = 18, color: str = "#ffffff") -> Optional[tk.PhotoImage]:
    """Obtiene un icono de Bootstrap si está disponible."""
    if not ICONS_AVAILABLE:
        return None
    try:
        return BootstrapIcon(name, size=size, color=color).image
    except Exception:
        return None


class LabeledEntry(tb.Frame):
    """Entrada con etiqueta."""

    def __init__(self, master, text_key: str, width: int = 10, **kwargs):
        super().__init__(master, **kwargs)
        self._text_key = text_key
        self.label = tb.Label(self, text=tr.get(text_key))
        self.entry = tb.Entry(self, width=width)
        self.label.pack(side=LEFT, padx=(0, 4))
        self.entry.pack(side=LEFT, fill=X, expand=True)
        tr.add_observer(self._refresh_ui)

    def _refresh_ui(self):
        self.label.configure(text=tr.get(self._text_key))

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class PathSelector(tb.Frame):
    """Selector de ruta de directorio con boton de exploracion."""

    def __init__(self, master, text_key: Optional[str] = None, initial: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self._text_key = text_key
        
        if self._text_key:
            self.label = tb.Label(self, text=tr.get(self._text_key))
            self.label.pack(side=LEFT, padx=(0, 4))
            
        self.var = tk.StringVar(value=initial)
        self.entry = tb.Entry(self, textvariable=self.var)

        self._icon_browse = _get_icon("folder")
        self.button = tb.Button(
            self,
            image=self._icon_browse if self._icon_browse else None,
            text=tr.get("ui.btn.browse") if not self._icon_browse else "",
            command=self._on_browse,
            bootstyle=SECONDARY,
        )

        self.entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 4))
        self.button.pack(side=LEFT)
        tr.add_observer(self._refresh_ui)

    def _refresh_ui(self):
        if self._text_key and hasattr(self, 'label'):
            self.label.configure(text=tr.get(self._text_key))
        if not self._icon_browse:
            self.button.configure(text=tr.get("ui.btn.browse"))

    def _on_browse(self):
        try:
            directory = filedialog.askdirectory()
            if directory:
                self.var.set(directory)
        except Exception:
            pass

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str):
        self.var.set(value)


class FileListPanel(tb.Frame):
    """Panel de lista de archivos con selección múltiple y botones de gestión."""

    def __init__(self, master, title_key: Optional[str] = None, **kwargs):
        super().__init__(master, **kwargs)
        self._files: List[Path] = []
        self._title_key = title_key
        self._build_ui()
        tr.add_observer(self._refresh_ui)

    def _build_ui(self):
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, pady=(0, 4))

        if self._title_key:
            self.title_label = tb.Label(header_frame, text=tr.get(self._title_key), font=("TkDefaultFont", 10, "bold"))
            self.title_label.pack(side=LEFT)

        btn_add_frame = tb.Frame(header_frame)
        btn_add_frame.pack(side=RIGHT)

        # Botón de ajustes (Gear) - Lado izquierdo de los botones de acción
        self._icon_gear = _get_icon("sliders")
        self.settings_btn = tb.Button(
            btn_add_frame,
            image=self._icon_gear if self._icon_gear else None,
            text="⚙" if not self._icon_gear else "",
            command=self._open_settings,
            bootstyle=SECONDARY,
        )
        self.settings_btn.pack(side=LEFT, padx=(0, 4))

        self._icon_folder = _get_icon("folder-plus")
        self._icon_file = _get_icon("file-earmark-plus")

        self.add_folder_btn = tb.Button(
            btn_add_frame,
            image=self._icon_folder if self._icon_folder else None,
            text=tr.get("ui.btn.add_folder") if not self._icon_folder else "",
            command=self._add_folder,
            bootstyle=SECONDARY,
            width=10 if not self._icon_folder else None,
        )
        self.add_folder_btn.pack(side=LEFT, padx=(2, 2))

        self.add_files_btn = tb.Button(
            btn_add_frame,
            image=self._icon_file if self._icon_file else None,
            text=tr.get("ui.btn.add_file") if not self._icon_file else "",
            command=self._add_files,
            bootstyle=SECONDARY,
            width=10 if not self._icon_file else None,
        )
        self.add_files_btn.pack(side=LEFT, padx=(2, 2))

        list_frame = tb.Frame(self, borderwidth=1, relief=SOLID)
        list_frame.pack(fill=BOTH, expand=True)

        scrollbar = tb.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self._listbox = tk.Listbox(
            list_frame,
            selectmode=EXTENDED,
            yscrollcommand=scrollbar.set,
            height=6,
        )
        self._listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self._listbox.yview)

        action_frame = tb.Frame(self)
        action_frame.pack(fill=X, pady=(4, 0))

        self._icon_trash = _get_icon("trash")
        self._icon_clear = _get_icon("arrow-counterclockwise")

        self.remove_btn = tb.Button(
            action_frame,
            image=self._icon_trash if self._icon_trash else None,
            text=tr.get("ui.btn.remove") if not self._icon_trash else "",
            command=self._remove_selected,
            bootstyle=DANGER,
            width=15 if not self._icon_trash else None,
        )
        self.remove_btn.pack(side=LEFT, padx=(2, 2))

        self.clear_btn = tb.Button(
            action_frame,
            image=self._icon_clear if self._icon_clear else None,
            text=tr.get("ui.btn.clear") if not self._icon_clear else "",
            command=self._clear_all,
            bootstyle=SECONDARY,
            width=10 if not self._icon_clear else None,
        )
        self.clear_btn.pack(side=RIGHT, padx=(2, 2))

    def _refresh_ui(self):
        if self._title_key and hasattr(self, 'title_label'):
            self.title_label.configure(text=tr.get(self._title_key))
        if not self._icon_folder: self.add_folder_btn.configure(text=tr.get("ui.btn.add_folder"))
        if not self._icon_file: self.add_files_btn.configure(text=tr.get("ui.btn.add_file"))
        if not self._icon_trash: self.remove_btn.configure(text=tr.get("ui.btn.remove"))
        if not self._icon_clear: self.clear_btn.configure(text=tr.get("ui.btn.clear"))

    def _open_settings(self):
        SettingsWindow(self.winfo_toplevel())

    def _add_folder(self):
        try:
            directory = filedialog.askdirectory()
            if not directory:
                return
            folder = Path(directory)
            if not folder.exists() or not folder.is_dir():
                return
            new_files = []
            try:
                for f in folder.iterdir():
                    if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                        new_files.append(f)
            except PermissionError:
                pass
            except OSError:
                pass
            self._add_files_list(new_files)
        except Exception:
            pass

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title=tr.get("ui.btn.add_file"),
            filetypes=[
                (tr.get("ui.btn.add_file"), " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)),
                ("All files", "*.*"),
            ],
        )
        if files:
            self._add_files_list([Path(f) for f in files])

    def _add_files_list(self, new_files: List[Path]):
        for f in new_files:
            if f not in self._files:
                self._files.append(f)
                self._listbox.insert(END, f.name)

    def _remove_selected(self):
        selected = self._listbox.curselection()
        if not selected:
            return
        for index in reversed(selected):
            self._files.pop(index)
            self._listbox.delete(index)

    def _clear_all(self):
        self._files.clear()
        self._listbox.delete(0, END)

    def get_files(self) -> List[Path]:
        return self._files.copy()

    def set_files(self, files: List[Path]):
        self._files = files.copy()
        self._listbox.delete(0, END)
        for f in files:
            self._listbox.insert(END, f.name)

    def clear(self):
        self._files.clear()
        self._listbox.delete(0, END)

    @property
    def count(self) -> int:
        return len(self._files)
