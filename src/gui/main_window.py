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
from ..utils.i18n import tr
from .validators import parse_positive_float, parse_optional_positive_float, validate_unit, validate_directories
from .components import PathSelector, FileListPanel, _get_icon


class MainWindow(tb.Window):
    """Ventana principal del procesador batch."""

    def __init__(self):
        super().__init__(themename="darkly")
        self.title(tr.get("ui.title"))
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
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        tr.add_observer(self._refresh_ui)

    def _on_closing(self):
        """Maneja el evento de cierre de ventana para evitar corrupcion de datos."""
        if self._processing_thread and self._processing_thread.is_alive():
            # Si hay un proceso activo, advertir al usuario
            result = Messagebox.show_question(
                message=tr.get("msg.close_confirm", default="Hay un proceso en curso. ¿Seguro que desea cancelar y salir?"),
                title=tr.get("msg.warning_title"),
                buttons=['No:No', 'Sí:Yes']
            )
            if result == "Yes":
                if self._batch_handler:
                    self._batch_handler.cancel()
                self.destroy()
        else:
            self.destroy()

    def _build_ui(self):
        main = tb.Frame(self, padding=10)
        main.pack(fill=BOTH, expand=True)

        self.input_frame = tb.Labelframe(main, text=tr.get("ui.label.input"), padding=10)
        self.input_frame.pack(fill=BOTH, expand=True, pady=(0, 8))

        self.file_list = FileListPanel(self.input_frame)
        self.file_list.pack(fill=BOTH, expand=True)

        self.output_frame = tb.Labelframe(main, text=tr.get("ui.label.output"), padding=10)
        self.output_frame.pack(fill=X, pady=(0, 8))

        self.output_selector = PathSelector(
            self.output_frame,
            initial=str(OUTPUT_DIR),
        )
        self.output_selector.pack(fill=X)

        self.size_frame = tb.Labelframe(main, text=tr.get("ui.label.params"), padding=10)
        self.size_frame.pack(fill=X, pady=(0, 8))

        self.notebook = tb.Notebook(self.size_frame, padding=5)
        self.notebook.pack(fill=X)
        self._build_basic_tab(self.notebook)
        self._build_advanced_tab(self.notebook)

        self._aspect_ratio: Optional[float] = None
        self._last_unit: str = "cm"
        self._updating_from_preset = False

        bottom_frame = tb.Frame(main)
        bottom_frame.pack(fill=BOTH, expand=True, pady=(4, 0))

        self.progress = tb.Progressbar(bottom_frame, mode="determinate")
        self.progress.pack(fill=X, pady=(0, 4))

        self.status_var = tk.StringVar(value=tr.get("ui.status.ready"))
        self.status_label = tb.Label(bottom_frame, textvariable=self.status_var, anchor=W)
        self.status_label.pack(fill=X, pady=(0, 4))

        btn_frame = tb.Frame(bottom_frame)
        btn_frame.pack(fill=X)

        self._setup_action_buttons(btn_frame)

    def _refresh_ui(self):
        """Actualiza todos los textos de la interfaz al cambiar el idioma."""
        self.title(tr.get("ui.title"))
        self.input_frame.configure(text=tr.get("ui.label.input"))
        self.output_frame.configure(text=tr.get("ui.label.output"))
        self.size_frame.configure(text=tr.get("ui.label.params"))
        
        self.notebook.tab(0, text=tr.get("ui.tab.basic"))
        self.notebook.tab(1, text=tr.get("ui.tab.advanced"))
        
        self.label_preset.configure(text=tr.get("ui.label.preset"))
        self.label_width.configure(text=tr.get("ui.label.width"))
        self.label_height.configure(text=tr.get("ui.label.height"))
        self.label_unit.configure(text=tr.get("ui.label.unit"))
        self.label_mode.configure(text=tr.get("ui.label.mode"))
        self.label_dpi.configure(text=tr.get("ui.label.dpi"))
        
        # Botones de acción
        if not self._icon_play: self.start_btn.configure(text=tr.get("ui.btn.start"))
        if not self._icon_cancel: self.cancel_btn.configure(text=tr.get("ui.btn.cancel"))
        if not self._icon_folder: self.detail_btn.configure(text=tr.get("ui.btn.open_output"))
        
        # Modos de combobox
        self.mode_cb.configure(values=(
            tr.get("ui.mode.fit"),
            tr.get("ui.mode.stretch"),
            tr.get("ui.mode.fill"),
            tr.get("ui.mode.crop"),
        ))
        
        # Resetear status si está en listo
        if self.status_var.get() in ("Listo", "Ready"):
            self.status_var.set(tr.get("ui.status.ready"))

    def _build_basic_tab(self, notebook):
        basic_frame = tb.Frame(notebook, padding=5)
        notebook.add(basic_frame, text=tr.get("ui.tab.basic"), sticky="nwse")

        basic_inner = tb.Frame(basic_frame)
        basic_inner.pack(fill=X)

        self.label_preset = tb.Label(basic_inner, text=tr.get("ui.label.preset"))
        self.label_preset.grid(row=0, column=0, sticky=W, padx=2, pady=3)
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

        self.label_width = tb.Label(basic_inner, text=tr.get("ui.label.width"))
        self.label_width.grid(row=1, column=0, sticky=W, padx=2, pady=3)
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

        self.label_height = tb.Label(basic_inner, text=tr.get("ui.label.height"))
        self.label_height.grid(row=2, column=0, sticky=W, padx=2, pady=3)
        self.height_entry = tb.Entry(basic_inner, width=10)
        self.height_entry.grid(row=2, column=1, sticky=W, padx=2, pady=3)
        self.height_entry.bind("<KeyRelease>", self._on_height_changed)

        self.label_unit = tb.Label(basic_inner, text=tr.get("ui.label.unit"))
        self.label_unit.grid(row=3, column=0, sticky=W, padx=2, pady=3)
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
        notebook.add(advanced_frame, text=tr.get("ui.tab.advanced"), sticky="nwse")

        advanced_inner = tb.Frame(advanced_frame)
        advanced_inner.pack(fill=X)

        self.label_mode = tb.Label(advanced_inner, text=tr.get("ui.label.mode"))
        self.label_mode.grid(row=0, column=0, sticky=W, padx=2, pady=3)
        self.mode_var = tk.StringVar(value=tr.get("ui.mode.fit"))
        self.mode_cb = tb.Combobox(
            advanced_inner,
            textvariable=self.mode_var,
            values=(
                tr.get("ui.mode.fit"),
                tr.get("ui.mode.stretch"),
                tr.get("ui.mode.fill"),
                tr.get("ui.mode.crop"),
            ),
            state="readonly",
            width=18,
        )
        self.mode_cb.grid(row=0, column=1, columnspan=2, sticky=W, padx=2, pady=3)

        self.label_dpi = tb.Label(advanced_inner, text=tr.get("ui.label.dpi"))
        self.label_dpi.grid(row=1, column=0, sticky=W, padx=2, pady=3)
        self.dpi_var = tk.StringVar(value=str(DEFAULT_DPI))
        self.dpi_entry = tb.Entry(advanced_inner, width=10, textvariable=self.dpi_var)
        self.dpi_entry.grid(row=1, column=1, columnspan=2, sticky=W, padx=2, pady=3)

    def _setup_action_buttons(self, parent: tb.Frame):
        self._icon_play = _get_icon("play-fill", size=18, color="#ffffff")
        self._icon_cancel = _get_icon("x", size=18, color="#ffffff")
        self._icon_folder = _get_icon("folder2-open", size=18, color="#ffffff")

        self.start_btn = tb.Button(
            parent,
            image=self._icon_play if self._icon_play else None,
            text=tr.get("ui.btn.start") if not self._icon_play else "",
            bootstyle=SUCCESS,
            command=self._on_start,
        )
        self.start_btn.pack(side=LEFT, padx=(0, 4))

        self.cancel_btn = tb.Button(
            parent,
            image=self._icon_cancel if self._icon_cancel else None,
            text=tr.get("ui.btn.cancel") if not self._icon_cancel else "",
            bootstyle=DANGER,
            command=self._on_cancel,
            state=DISABLED,
        )
        self.cancel_btn.pack(side=LEFT, padx=(0, 4))

        self.detail_btn = tb.Button(
            parent,
            image=self._icon_folder if self._icon_folder else None,
            text=tr.get("ui.btn.open_output") if not self._icon_folder else "",
            bootstyle=SECONDARY,
            command=self._open_output_folder,
            state=DISABLED,
        )
        self.detail_btn.pack(side=LEFT, padx=(0, 4))

    def _map_mode(self) -> ResizeMode:
        text = self.mode_var.get()
        if text == tr.get("ui.mode.stretch"):
            return ResizeMode.STRETCH
        if text == tr.get("ui.mode.fit"):
            return ResizeMode.FIT
        if text == tr.get("ui.mode.fill"):
            return ResizeMode.FILL
        if text == tr.get("ui.mode.crop"):
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
            raise ValidationError(tr.get("err.empty_dpi"), code="EMPTY_DPI")
        try:
            dpi = int(dpi_str)
        except ValueError:
            raise ValidationError(tr.get("err.invalid_dpi"), code="INVALID_DPI_TYPE")
        if dpi <= 0:
            raise ValidationError(tr.get("err.invalid_dpi"), code="INVALID_DPI")

        w = parse_optional_positive_float(width_str, "ui.label.width")
        h = parse_optional_positive_float(height_str, "ui.label.height")

        if w is None and h is None:
            raise ValidationError(tr.get("err.missing_dims"), code="MISSING_DIMENSIONS")

        u = validate_unit(unit)
        out_path = validate_directories("", output_dir)[1]

        return out_path, w, h, u, u, dpi

    def _on_start(self):
        files = self.file_list.get_files()

        if not files:
            Messagebox.show_warning(
                title=tr.get("err.no_files"),
                message=tr.get("err.no_files_msg"),
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
            Messagebox.show_error(title=tr.get("err.validation"), message=str(e))
            return

        if not BatchHandler.validate_output_directory(output_dir):
            Messagebox.show_error(
                title=tr.get("msg.error_title"),
                message=tr.get("msg.cant_create_dir", error=tr.get("msg.permission_denied", path=str(output_dir)))
            )
            return

        self._processor.dpi = dpi

        self._total_files = len(files)
        self.progress["value"] = 0
        self.progress["maximum"] = self._total_files
        self.status_var.set(tr.get("ui.status.processing", current=0, total=self._total_files, file=""))
        
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
        self.status_var.set(tr.get("ui.status.cancelling"))
        self.cancel_btn.configure(state=DISABLED)

    def _on_progress_update(self, current: int, total: int, filename: str):
        def update():
            self.progress["value"] = current
            self.status_var.set(tr.get("ui.status.processing", current=current, total=total, file=filename))
            if current >= total:
                self.cancel_btn.configure(state=DISABLED)
                self.start_btn.configure(state=NORMAL)
        self.after(0, update)

    def _on_batch_finished(self, results):
        def finalize():
            ok = sum(1 for r in results if r.success)
            fail = len(results) - ok
            self.status_var.set(tr.get("ui.status.done", ok=ok, fail=fail))
            self.start_btn.configure(state=NORMAL)
            self.cancel_btn.configure(state=DISABLED)
            self.detail_btn.configure(state=NORMAL)
            if fail == 0:
                Messagebox.show_info(
                    title=tr.get("msg.done_title"),
                    message=tr.get("msg.done_success", ok=ok),
                )
            else:
                Messagebox.show_warning(
                    title=tr.get("msg.done_warn_title"),
                    message=tr.get("msg.done_warning", ok=ok, fail=fail),
                )
        self.after(0, finalize)

    def _on_batch_error(self, error_message: str):
        def handle_error():
            self.status_var.set(f"Error: {error_message}")
            self.start_btn.configure(state=NORMAL)
            self.cancel_btn.configure(state=DISABLED)
            self.detail_btn.configure(state=DISABLED)
            Messagebox.show_error(
                title=tr.get("msg.error_title"),
                message=tr.get("err.unexpected", error=error_message)
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
            except Exception as e:
                Messagebox.show_error(title=tr.get("msg.error_title"), message=str(e))
                return
        self._open_folder_crossplatform(output_path)

    def _open_folder_crossplatform(self, path: Path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.Popen(['xdg-open' if 'linux' in os.sys.platform else 'open', str(path)])
        except Exception:
            pass


def run():
    app = MainWindow()
    app.mainloop()
