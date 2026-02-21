"""Ventana principal de la aplicacion."""

import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from typing import List, Optional

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from ..core import BatchHandler, ImageProcessor, ResizeMode, UnitConverter
from ..utils import (
    DEFAULT_DPI,
    DEFAULT_OUTPUT_SUFFIX,
    OUTPUT_DIR,
    ValidationError,
    get_all_preset_names,
    get_preset_by_name,
    search_preset_names,
    SizePreset,
    load_window_icon,
)
from .validators import parse_positive_float, parse_optional_positive_float, validate_unit, validate_directories
from .components import PathSelector, FileListPanel, _get_icon


class MainWindow(tb.Window):
    """Ventana principal del procesador batch."""

    def __init__(self):
        super().__init__(themename="darkly")
        self.title("PycResizer")
        self.geometry("500x650")
        self.resizable(False, True)

        load_window_icon(self)

        self._build_ui()

        self._processor = ImageProcessor(dpi=DEFAULT_DPI)
        self._batch_handler: BatchHandler = BatchHandler(
            processor=self._processor,
            max_workers=0,
            progress_callback=self._on_progress_update,
        )
        self._processing_thread = None
        self._total_files: int = 0

    def _build_ui(self):
        main = tb.Frame(self, padding=10)
        main.pack(fill=BOTH, expand=True)

        input_frame = tb.Labelframe(main, text="Archivos de entrada", padding=10)
        input_frame.pack(fill=BOTH, expand=True, pady=(0, 8))

        self.file_list = FileListPanel(input_frame, title="Archivos seleccionados")
        self.file_list.pack(fill=BOTH, expand=True)

        output_frame = tb.Labelframe(main, text="Carpeta de salida", padding=10)
        output_frame.pack(fill=X, pady=(0, 8))

        self.output_selector = PathSelector(
            output_frame,
            text="Salida:",
            initial=str(OUTPUT_DIR),
        )
        self.output_selector.pack(fill=X)

        size_frame = tb.Labelframe(main, text="Parametros", padding=10)
        size_frame.pack(fill=X, pady=(0, 8))

        try:
            notebook = tb.Notebook(size_frame, padding=5)
            notebook.pack(fill=X)
            self._build_basic_tab(notebook)
            self._build_advanced_tab(notebook)
        except Exception:
            self._build_params_legacy(size_frame)

        self._aspect_ratio: Optional[float] = None
        self._last_unit: str = "cm"
        self._updating_from_preset = False

        bottom_frame = tb.Frame(main)
        bottom_frame.pack(fill=BOTH, expand=True, pady=(4, 0))

        self.progress = tb.Progressbar(bottom_frame, mode="determinate")
        self.progress.pack(fill=X, pady=(0, 4))

        self.status_var = tk.StringVar(value="Listo")
        self.status_label = tb.Label(bottom_frame, textvariable=self.status_var, anchor=W)
        self.status_label.pack(fill=X, pady=(0, 4))

        btn_frame = tb.Frame(bottom_frame)
        btn_frame.pack(fill=X)

        self._setup_action_buttons(btn_frame)

        self._last_results: List = []

    def _build_basic_tab(self, notebook):
        basic_frame = tb.Frame(notebook, padding=5)
        notebook.add(basic_frame, text=" Basico ", sticky="nwse")

        basic_inner = tb.Frame(basic_frame)
        basic_inner.pack(fill=X)

        tb.Label(basic_inner, text="Preset:").grid(row=0, column=0, sticky=W, padx=2, pady=3)
        self.preset_var = tk.StringVar(value="")
        self.preset_cb = tb.Combobox(
            basic_inner,
            textvariable=self.preset_var,
            values=get_all_preset_names(),
            width=22,
            state="normal",
        )
        self.preset_cb.grid(row=0, column=1, columnspan=2, sticky=W, padx=2, pady=3)
        self.preset_cb.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.preset_cb.bind("<KeyRelease>", self._on_preset_search)
        self.preset_cb.bind("<FocusIn>", self._on_preset_focus)

        tb.Label(basic_inner, text="Ancho:").grid(row=1, column=0, sticky=W, padx=2, pady=3)
        self.width_entry = tb.Entry(basic_inner, width=10)
        self.width_entry.grid(row=1, column=1, sticky=W, padx=2, pady=3)
        self.width_entry.bind("<KeyRelease>", self._on_width_changed)

        self._chain_var = tk.BooleanVar(value=False)
        icon_chain = _get_icon("link", size=16, color="#ffffff")
        if icon_chain:
            self._chain_btn = tb.Checkbutton(
                basic_inner,
                image=icon_chain,
                variable=self._chain_var,
                command=self._on_chain_toggled,
            )
        else:
            self._chain_btn = tb.Checkbutton(
                basic_inner,
                text="🔗",
                variable=self._chain_var,
                command=self._on_chain_toggled,
            )
        self._chain_btn.grid(row=1, column=2, sticky=W, padx=2, pady=3)

        tb.Label(basic_inner, text="Alto:").grid(row=2, column=0, sticky=W, padx=2, pady=3)
        self.height_entry = tb.Entry(basic_inner, width=10)
        self.height_entry.grid(row=2, column=1, sticky=W, padx=2, pady=3)
        self.height_entry.bind("<KeyRelease>", self._on_height_changed)

        tb.Label(basic_inner, text="Unidad:").grid(row=3, column=0, sticky=W, padx=2, pady=3)
        self.unit_var = tk.StringVar(value="cm")
        self.unit_cb = tb.Combobox(
            basic_inner,
            textvariable=self.unit_var,
            values=("px", "cm", "mm", "in"),
            width=10,
            state="readonly",
        )
        self.unit_cb.grid(row=3, column=1, sticky=W, padx=2, pady=3)
        self.unit_cb.bind("<<ComboboxSelected>>", self._on_unit_changed)

    def _build_advanced_tab(self, notebook):
        advanced_frame = tb.Frame(notebook, padding=5)
        notebook.add(advanced_frame, text=" Avanzado ", sticky="nwse")

        advanced_inner = tb.Frame(advanced_frame)
        advanced_inner.pack(fill=X)

        tb.Label(advanced_inner, text="Modo:").grid(row=0, column=0, sticky=W, padx=2, pady=3)
        self.mode_var = tk.StringVar(value="Ajustar (fit)")
        self.mode_cb = tb.Combobox(
            advanced_inner,
            textvariable=self.mode_var,
            values=(
                "Ajustar (fit)",
                "Estirar",
                "Rellenar (fill)",
                "Recortar (crop)",
            ),
            state="readonly",
            width=18,
        )
        self.mode_cb.grid(row=0, column=1, columnspan=2, sticky=W, padx=2, pady=3)

        tb.Label(advanced_inner, text="DPI:").grid(row=1, column=0, sticky=W, padx=2, pady=3)
        self.dpi_var = tk.StringVar(value=str(DEFAULT_DPI))
        self.dpi_entry = tb.Entry(advanced_inner, width=10, textvariable=self.dpi_var)
        self.dpi_entry.grid(row=1, column=1, columnspan=2, sticky=W, padx=2, pady=3)

    def _build_params_legacy(self, parent):
        size_inner = tb.Frame(parent, padding=10)
        size_inner.pack(fill=X)

        tb.Label(size_inner, text="Preset:").grid(row=0, column=0, sticky=W, padx=2, pady=2)
        self.preset_var = tk.StringVar(value="")
        self.preset_cb = tb.Combobox(
            size_inner,
            textvariable=self.preset_var,
            values=get_all_preset_names(),
            width=22,
            state="normal",
        )
        self.preset_cb.grid(row=0, column=1, columnspan=2, sticky=W, padx=2, pady=2)
        self.preset_cb.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.preset_cb.bind("<KeyRelease>", self._on_preset_search)
        self.preset_cb.bind("<FocusIn>", self._on_preset_focus)

        tb.Label(size_inner, text="Ancho:").grid(row=1, column=0, sticky=W, padx=2, pady=2)
        self.width_entry = tb.Entry(size_inner, width=10)
        self.width_entry.grid(row=1, column=1, sticky=W, padx=2, pady=2)
        self.width_entry.bind("<KeyRelease>", self._on_width_changed)

        self._chain_var = tk.BooleanVar(value=False)
        icon_chain = _get_icon("link", size=16, color="#ffffff")
        if icon_chain:
            self._chain_btn = tb.Checkbutton(
                size_inner,
                image=icon_chain,
                variable=self._chain_var,
                command=self._on_chain_toggled,
            )
        else:
            self._chain_btn = tb.Checkbutton(
                size_inner,
                text="🔗",
                variable=self._chain_var,
                command=self._on_chain_toggled,
            )
        self._chain_btn.grid(row=1, column=2, sticky=W, padx=2, pady=2)

        tb.Label(size_inner, text="Alto:").grid(row=2, column=0, sticky=W, padx=2, pady=2)
        self.height_entry = tb.Entry(size_inner, width=10)
        self.height_entry.grid(row=2, column=1, sticky=W, padx=2, pady=2)
        self.height_entry.bind("<KeyRelease>", self._on_height_changed)

        tb.Label(size_inner, text="Unidad:").grid(row=3, column=0, sticky=W, padx=2, pady=2)
        self.unit_var = tk.StringVar(value="cm")
        self.unit_cb = tb.Combobox(
            size_inner,
            textvariable=self.unit_var,
            values=("px", "cm", "mm", "in"),
            width=10,
            state="readonly",
        )
        self.unit_cb.grid(row=3, column=1, sticky=W, padx=2, pady=2)
        self.unit_cb.bind("<<ComboboxSelected>>", self._on_unit_changed)

        tb.Label(size_inner, text="Modo:").grid(row=4, column=0, sticky=W, padx=2, pady=2)
        self.mode_var = tk.StringVar(value="Ajustar (fit)")
        self.mode_cb = tb.Combobox(
            size_inner,
            textvariable=self.mode_var,
            values=(
                "Ajustar (fit)",
                "Estirar",
                "Rellenar (fill)",
                "Recortar (crop)",
            ),
            state="readonly",
            width=18,
        )
        self.mode_cb.grid(row=4, column=1, columnspan=2, sticky=W, padx=2, pady=2)

        tb.Label(size_inner, text="DPI:").grid(row=5, column=0, sticky=W, padx=2, pady=2)
        self.dpi_var = tk.StringVar(value=str(DEFAULT_DPI))
        self.dpi_entry = tb.Entry(size_inner, width=10, textvariable=self.dpi_var)
        self.dpi_entry.grid(row=5, column=1, columnspan=2, sticky=W, padx=2, pady=2)

    def _setup_action_buttons(self, parent: tb.Frame):
        icon_play = _get_icon("play-fill", size=18, color="#ffffff")
        icon_cancel = _get_icon("x", size=18, color="#ffffff")
        icon_folder = _get_icon("folder2-open", size=18, color="#ffffff")

        if icon_play:
            self.start_btn = tb.Button(
                parent,
                image=icon_play,
                bootstyle=SUCCESS,
                command=self._on_start,
            )
        else:
            self.start_btn = tb.Button(
                parent,
                text="Iniciar",
                bootstyle=SUCCESS,
                command=self._on_start,
            )
        self.start_btn.pack(side=LEFT, padx=(0, 4))

        if icon_cancel:
            self.cancel_btn = tb.Button(
                parent,
                image=icon_cancel,
                bootstyle=DANGER,
                command=self._on_cancel,
                state=DISABLED,
            )
        else:
            self.cancel_btn = tb.Button(
                parent,
                text="Cancelar",
                bootstyle=DANGER,
                command=self._on_cancel,
                state=DISABLED,
            )
        self.cancel_btn.pack(side=LEFT, padx=(0, 4))

        if icon_folder:
            self.detail_btn = tb.Button(
                parent,
                image=icon_folder,
                bootstyle=SECONDARY,
                command=self._open_output_folder,
                state=DISABLED,
            )
        else:
            self.detail_btn = tb.Button(
                parent,
                text="Abrir output",
                bootstyle=SECONDARY,
                command=self._open_output_folder,
                state=DISABLED,
            )
        self.detail_btn.pack(side=LEFT, padx=(0, 4))

    def _map_mode(self) -> ResizeMode:
        text = self.mode_var.get()
        if text.startswith("Estirar"):
            return ResizeMode.STRETCH
        if text.startswith("Ajustar"):
            return ResizeMode.FIT
        if text.startswith("Rellenar"):
            return ResizeMode.FILL
        if text.startswith("Recortar"):
            return ResizeMode.CROP
        return ResizeMode.FIT

    def _on_preset_focus(self, event=None):
        self.preset_cb['values'] = get_all_preset_names()

    def _on_preset_search(self, event=None):
        query = self.preset_var.get()
        if not query:
            self.preset_cb['values'] = get_all_preset_names()
        else:
            results = search_preset_names(query)
            self.preset_cb['values'] = results

    def _on_preset_selected(self, event=None):
        preset_name = self.preset_var.get()
        if not preset_name:
            return
        
        try:
            preset: SizePreset = get_preset_by_name(preset_name)
            self._updating_from_preset = True
            
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(preset.width))
            
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(preset.height))
            
            self.unit_var.set(preset.unit)
            self._last_unit = preset.unit
            
            self._aspect_ratio = preset.width / preset.height
            
            self._updating_from_preset = False
            
            if self._chain_var.get():
                self._chain_var.set(False)
                
        except Exception as e:
            self._updating_from_preset = False

    def _on_unit_changed(self, event=None):
        if self._updating_from_preset:
            return
        
        try:
            new_unit = self.unit_var.get()
            old_unit = getattr(self, '_last_unit', 'cm')
            
            if new_unit == old_unit:
                self._last_unit = new_unit
                return
            
            w_str = self.width_entry.get().strip()
            h_str = self.height_entry.get().strip()
            
            if not w_str or not h_str:
                self._last_unit = new_unit
                return
            
            w = float(w_str)
            h = float(h_str)
            dpi = self._get_current_dpi()
            
            w_px = UnitConverter.to_pixels(w, old_unit, dpi)
            h_px = UnitConverter.to_pixels(h, old_unit, dpi)
            
            w_new = UnitConverter.from_pixels(w_px, new_unit, dpi)
            h_new = UnitConverter.from_pixels(h_px, new_unit, dpi)
            
            self._updating_from_preset = True
            
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, f"{w_new:.2f}")
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, f"{h_new:.2f}")
            
            self._last_unit = new_unit
            self._updating_from_preset = False
            
        except Exception:
            self._updating_from_preset = False

    def _get_current_dpi(self) -> int:
        try:
            dpi_str = self.dpi_var.get().strip()
            if dpi_str:
                dpi = int(dpi_str)
                if dpi > 0:
                    return dpi
        except Exception:
            pass
        return DEFAULT_DPI

    def _on_chain_toggled(self):
        if self._chain_var.get():
            try:
                w_str = self.width_entry.get().strip()
                h_str = self.height_entry.get().strip()
                
                if w_str and h_str:
                    w = float(w_str)
                    h = float(h_str)
                    if w > 0 and h > 0:
                        self._aspect_ratio = w / h
                    else:
                        self._chain_var.set(False)
                else:
                    self._chain_var.set(False)
            except ValueError:
                self._chain_var.set(False)

    def _on_width_changed(self, event=None):
        if not self._chain_var.get() or self._updating_from_preset:
            return
        
        if self._aspect_ratio is None:
            try:
                w_str = self.width_entry.get().strip()
                h_str = self.height_entry.get().strip()
                if w_str and h_str:
                    w = float(w_str)
                    h = float(h_str)
                    if w > 0 and h > 0:
                        self._aspect_ratio = w / h
            except ValueError:
                return
        
        try:
            w_str = self.width_entry.get().strip()
            if w_str:
                w = float(w_str)
                if w > 0 and self._aspect_ratio:
                    new_h = w / self._aspect_ratio
                    self.height_entry.delete(0, tk.END)
                    self.height_entry.insert(0, f"{new_h:.2f}")
        except ValueError:
            pass

    def _on_height_changed(self, event=None):
        if not self._chain_var.get() or self._updating_from_preset:
            return
        
        if self._aspect_ratio is None:
            try:
                w_str = self.width_entry.get().strip()
                h_str = self.height_entry.get().strip()
                if w_str and h_str:
                    w = float(w_str)
                    h = float(h_str)
                    if w > 0 and h > 0:
                        self._aspect_ratio = w / h
            except ValueError:
                return
        
        try:
            h_str = self.height_entry.get().strip()
            if h_str:
                h = float(h_str)
                if h > 0 and self._aspect_ratio:
                    new_w = h * self._aspect_ratio
                    self.width_entry.delete(0, tk.END)
                    self.width_entry.insert(0, f"{new_w:.2f}")
        except ValueError:
            pass

    def _validate_inputs(self):
        output_dir = self.output_selector.get()

        width_str = self.width_entry.get()
        height_str = self.height_entry.get()
        unit = self.unit_var.get()

        dpi_str = self.dpi_var.get().strip()
        if not dpi_str:
            raise ValidationError("DPI no puede estar vacio", code="EMPTY_DPI")
        try:
            dpi = int(dpi_str)
        except ValueError:
            raise ValidationError("DPI debe ser entero", code="INVALID_DPI_TYPE")
        if dpi <= 0:
            raise ValidationError("DPI debe ser mayor que cero", code="INVALID_DPI")

        w = parse_optional_positive_float(width_str, "Ancho")
        h = parse_optional_positive_float(height_str, "Alto")

        if w is None and h is None:
            raise ValidationError(
                "Debe especificar al menos una dimension (ancho o alto)",
                code="MISSING_DIMENSIONS"
            )

        u = validate_unit(unit)

        out_path = validate_directories("", output_dir)[1]

        return out_path, w, h, u, u, dpi

    def _on_start(self):
        files = self.file_list.get_files()

        if not files:
            Messagebox.show_warning(
                title="Sin archivos",
                message="No hay archivos seleccionados. Añade archivos o una carpeta.",
            )
            return

        try:
            (
                output_dir,
                width,
                height,
                unit,
                unit,
                dpi,
            ) = self._validate_inputs()
        except ValidationError as e:
            Messagebox.show_error(title="Error de validacion", message=str(e))
            return

        self._processor.dpi = dpi

        self._total_files = len(files)
        self.progress["value"] = 0
        self.progress["maximum"] = self._total_files
        self.status_var.set(f"Procesando 0 / {self._total_files}")
        self._last_results = []

        self.start_btn.configure(state=DISABLED)
        self.cancel_btn.configure(state=NORMAL)
        self.detail_btn.configure(state=DISABLED)

        mode = self._map_mode()

        def run_batch():
            try:
                handler = BatchHandler(
                    processor=self._processor,
                    max_workers=0,
                    progress_callback=self._on_progress_update,
                )
                self._batch_handler = handler
                results = handler.process_batch(
                    input_files=files,
                    output_dir=output_dir,
                    width=width,
                    height=height,
                    width_unit=unit,
                    height_unit=unit,
                    mode=mode,
                    suffix=DEFAULT_OUTPUT_SUFFIX,
                )
                self._on_batch_finished(results)
            except Exception as e:
                self._on_batch_error(str(e))

        self._processing_thread = threading.Thread(target=run_batch, daemon=True)
        self._processing_thread.start()

    def _on_cancel(self):
        if self._batch_handler:
            self._batch_handler.cancel()
        self.status_var.set("Cancelando...")
        self.cancel_btn.configure(state=DISABLED)

    def _on_progress_update(self, current: int, total: int, filename: str):
        def update():
            self.progress["value"] = current
            self.status_var.set(f"{current} / {total} - {filename}")
            if current >= total:
                self.cancel_btn.configure(state=DISABLED)
                self.start_btn.configure(state=NORMAL)
        self.after(0, update)

    def _on_batch_finished(self, results):
        def finalize():
            self._last_results = results
            ok = sum(1 for r in results if r.success)
            fail = len(results) - ok
            self.status_var.set(f"Completado. OK: {ok}, Fallos: {fail}")
            self.start_btn.configure(state=NORMAL)
            self.cancel_btn.configure(state=DISABLED)
            self.detail_btn.configure(state=NORMAL)
            if fail == 0:
                Messagebox.show_info(
                    title="Completado",
                    message=f"Procesamiento finalizado. {ok} archivos procesados correctamente.",
                )
            else:
                Messagebox.show_warning(
                    title="Completado con advertencias",
                    message=f"Procesamiento finalizado. OK: {ok}, Fallos: {fail}",
                )
        self.after(0, finalize)

    def _on_batch_error(self, error_message: str):
        def handle_error():
            self.status_var.set(f"Error: {error_message}")
            self.start_btn.configure(state=NORMAL)
            self.cancel_btn.configure(state=DISABLED)
            self.detail_btn.configure(state=DISABLED)
            Messagebox.show_error(
                title="Error",
                message=f"Error durante el procesamiento:\n{error_message}"
            )
        self.after(0, handle_error)

    def _get_output_path(self) -> Path:
        output_dir = self.output_selector.get().strip()
        if not output_dir:
            return OUTPUT_DIR
        return Path(output_dir)

    def _open_output_folder(self):
        output_path = self._get_output_path()
        
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                Messagebox.show_error(
                    title="Error",
                    message=f"No se pudo crear el directorio de salida:\n{output_path}\n\nError: {str(e)}"
                )
                return
        
        if not output_path.is_dir():
            Messagebox.show_error(
                title="Error",
                message=f"La ruta de salida no es un directorio válido:\n{output_path}"
            )
            return
        
        self._open_folder_crossplatform(output_path)

    def _open_folder_crossplatform(self, path: Path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                if 'darwin' in os.uname().sysname.lower():
                    subprocess.Popen(['open', str(path)])
                else:
                    subprocess.Popen(['xdg-open', str(path)])
            else:
                Messagebox.show_warning(
                    title="Advertencia",
                    message=f"No se puede abrir automáticamente el explorador en este sistema.\n\nRuta: {path}"
                )
        except FileNotFoundError:
            Messagebox.show_error(
                title="Error",
                message=f"No se encontró el programa para abrir carpetas.\n\nRuta: {path}"
            )
        except PermissionError:
            Messagebox.show_error(
                title="Error",
                message=f"Permiso denegado para acceder a:\n{path}"
            )
        except OSError as e:
            Messagebox.show_error(
                title="Error",
                message=f"Error del sistema al abrir la carpeta:\n{str(e)}"
            )


def run():
    app = MainWindow()
    app.mainloop()
