# src/gui/settings_window.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ..utils.i18n import tr
from ..utils import load_window_icon

class SettingsWindow(tb.Toplevel):
    def __init__(self, master):
        super().__init__(title=tr.get("settings.title"), size=(350, 120), resizable=(False, False))
        self.master = master
        
        load_window_icon(self)
        
        self.position_center()
        self.grab_set()  # Hacer ventana modal
        
        container = tb.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)
        
        self.label = tb.Label(container, text=tr.get("settings.lang"))
        self.label.pack(side=LEFT, padx=(0, 10))
        
        # Mapeo legible de idiomas
        self.langs = {"Español": "es", "English": "en"}
        current_display = "Español" if tr.current_lang == "es" else "English"
        
        self.lang_var = tb.StringVar(value=current_display)
        self.lang_cb = tb.Combobox(
            container, 
            textvariable=self.lang_var,
            values=list(self.langs.keys()),
            state="readonly",
            width=15
        )
        self.lang_cb.pack(side=LEFT)
        self.lang_cb.bind("<<ComboboxSelected>>", self._on_lang_change)

        tr.add_observer(self._refresh_ui)

    def _on_lang_change(self, event):
        selection = self.lang_var.get()
        new_lang = self.langs.get(selection, "es")
        tr.set_language(new_lang)

    def _refresh_ui(self):
        self.title(tr.get("settings.title"))
        self.label.configure(text=tr.get("settings.lang"))

    def position_center(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        # Intentar centrar respecto a la ventana principal si está disponible
        try:
            main_x = self.master.winfo_x()
            main_y = self.master.winfo_y()
            main_w = self.master.winfo_width()
            main_h = self.master.winfo_height()
            x = main_x + (main_w // 2) - (width // 2)
            y = main_y + (main_h // 2) - (height // 2)
        except Exception:
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            
        self.geometry(f'{width}x{height}+{max(0, x)}+{max(0, y)}')
