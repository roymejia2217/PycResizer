"""Componentes reutilizables de la GUI."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import List, Optional

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..utils import SUPPORTED_EXTENSIONS

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

    def __init__(self, master, text: str, width: int = 10, **kwargs):
        super().__init__(master, **kwargs)
        self.label = tb.Label(self, text=text)
        self.entry = tb.Entry(self, width=width)
        self.label.pack(side=LEFT, padx=(0, 4))
        self.entry.pack(side=LEFT, fill=X, expand=True)

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class PathSelector(tb.Frame):
    """Selector de ruta de directorio con boton de exploracion."""

    def __init__(self, master, text: str, initial: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.label = tb.Label(self, text=text)
        self.var = tk.StringVar(value=initial)
        self.entry = tb.Entry(self, textvariable=self.var)

        icon = _get_icon("folder")
        if icon:
            self.button = tb.Button(
                self,
                image=icon,
                command=self._on_browse,
                bootstyle=SECONDARY,
            )
        else:
            self.button = tb.Button(
                self,
                text="Examinar",
                command=self._on_browse,
                bootstyle=SECONDARY,
            )

        self.label.pack(side=LEFT, padx=(0, 4))
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 4))
        self.button.pack(side=LEFT)

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

    def __init__(self, master, title: str = "Archivos seleccionados", **kwargs):
        super().__init__(master, **kwargs)
        self._files: List[Path] = []

        self._build_ui(title)

    def _build_ui(self, title: str):
        header_frame = tb.Frame(self)
        header_frame.pack(fill=X, pady=(0, 4))

        tb.Label(header_frame, text=title, font=("TkDefaultFont", 10, "bold")).pack(side=LEFT)

        btn_add_frame = tb.Frame(header_frame)
        btn_add_frame.pack(side=RIGHT)

        icon_folder = _get_icon("folder-plus")
        icon_file = _get_icon("file-earmark-plus")

        if icon_folder:
            tb.Button(
                btn_add_frame,
                image=icon_folder,
                command=self._add_folder,
                bootstyle=SECONDARY,
            ).pack(side=LEFT, padx=(2, 2))
        else:
            tb.Button(
                btn_add_frame,
                text="+ Carpeta",
                command=self._add_folder,
                bootstyle=SECONDARY,
                width=10,
            ).pack(side=LEFT, padx=(0, 2))

        if icon_file:
            tb.Button(
                btn_add_frame,
                image=icon_file,
                command=self._add_files,
                bootstyle=SECONDARY,
            ).pack(side=LEFT, padx=(2, 2))
        else:
            tb.Button(
                btn_add_frame,
                text="+ Archivos",
                command=self._add_files,
                bootstyle=SECONDARY,
                width=10,
            ).pack(side=LEFT)

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

        icon_trash = _get_icon("trash")
        icon_clear = _get_icon("arrow-counterclockwise")

        if icon_trash:
            tb.Button(
                action_frame,
                image=icon_trash,
                command=self._remove_selected,
                bootstyle=DANGER,
            ).pack(side=LEFT, padx=(2, 2))
        else:
            tb.Button(
                action_frame,
                text="Eliminar",
                command=self._remove_selected,
                bootstyle=DANGER,
                width=15,
            ).pack(side=LEFT)

        if icon_clear:
            tb.Button(
                action_frame,
                image=icon_clear,
                command=self._clear_all,
                bootstyle=SECONDARY,
            ).pack(side=RIGHT, padx=(2, 2))
        else:
            tb.Button(
                action_frame,
                text="Limpiar",
                command=self._clear_all,
                bootstyle=SECONDARY,
                width=10,
            ).pack(side=RIGHT)

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
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)),
                ("Todos los archivos", "*.*"),
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
