"""Motor de internacionalizacion."""

import tkinter as tk
from typing import Dict, Any, List, Callable

_TRANSLATIONS = {
    "es": {
        "ui.title": "PycResizer",
        "ui.tab.basic": " Básico ",
        "ui.tab.advanced": " Avanzado ",
        "ui.label.input": "Archivos de entrada",
        "ui.label.output": "Carpeta de salida",
        "ui.label.params": "Parámetros",
        "ui.label.preset": "Preset:",
        "ui.label.width": "Ancho:",
        "ui.label.height": "Alto:",
        "ui.label.unit": "Unidad:",
        "ui.label.mode": "Modo:",
        "ui.label.dpi": "DPI:",
        "ui.btn.start": "Iniciar",
        "ui.btn.cancel": "Cancelar",
        "ui.btn.open_output": "Abrir salida",
        "ui.btn.browse": "Examinar",
        "ui.btn.add_file": "Archivos",
        "ui.btn.add_folder": "Carpeta",
        "ui.btn.remove": "Eliminar",
        "ui.btn.clear": "Limpiar",
        "ui.status.ready": "Listo",
        "ui.status.processing": "{current} / {total} - {file}",
        "ui.status.cancelling": "Cancelando...",
        "ui.status.done": "Completado. OK: {ok}, Fallos: {fail}",
        "ui.mode.fit": "Ajustar (fit)",
        "ui.mode.stretch": "Estirar",
        "ui.mode.fill": "Rellenar (fill)",
        "ui.mode.crop": "Recortar (crop)",
        "err.empty_dpi": "DPI no puede estar vacío",
        "err.invalid_dpi": "DPI debe ser mayor que cero",
        "err.invalid_dpi_type": "DPI debe ser numérico",
        "err.no_files": "Sin archivos",
        "err.no_files_msg": "No hay archivos seleccionados. Añade archivos o una carpeta.",
        "err.validation": "Error de validación",
        "err.missing_dims": "Debe especificar al menos una dimensión",
        "err.io_error": "Error al procesar imagen: {error}",
        "err.unexpected": "Error inesperado: {error}",
        "err.empty_value": "{field} no puede estar vacío",
        "err.not_numeric": "{field} debe ser numérico",
        "err.non_positive": "{field} debe ser mayor que cero",
        "err.invalid_unit": "Unidad no válida: {unit}",
        "err.invalid_input_dir": "Directorio de entrada inválido: {path}",
        "err.file_not_found": "Archivo no existe: {path}",
        "err.unsupported_format": "Formato no soportado: {ext}",
        "err.invalid_dimensions": "Dimensiones deben ser mayores que cero",
        "err.negative_value": "El valor no puede ser negativo",
        "err.conversion_failed": "Error al convertir {value}{unit}: {error}",
        "err.unsupported_unit": "Conversión no implementada: {unit}",
        "err.negative_pixels": "Los píxeles no pueden ser negativos",
        "err.dir_not_found": "Directorio no existe: {dir}",
        "err.process_cancelled": "Proceso cancelado",
        "msg.done_success": "Procesamiento finalizado. {ok} archivos procesados correctamente.",
        "msg.done_warning": "Procesamiento finalizado con advertencias. OK: {ok}, Fallos: {fail}",
        "msg.done_title": "Completado",
        "msg.done_warn_title": "Completado con advertencias",
        "msg.error_title": "Error",
        "msg.warning_title": "Advertencia",
        "msg.cant_create_dir": "No se pudo crear directorio de salida: {error}",
        "msg.invalid_out_dir": "La ruta de salida no es un directorio válido:\n{path}",
        "msg.cant_open_dir": "No se puede abrir automáticamente el explorador en este sistema.\n\nRuta: {path}",
        "msg.no_program_dir": "No se encontró el programa para abrir carpetas.\n\nRuta: {path}",
        "msg.permission_denied": "Permiso denegado para acceder a:\n{path}",
        "msg.sys_error_dir": "Error del sistema al abrir la carpeta:\n{error}",
        "msg.close_confirm": "Hay un proceso en curso. ¿Seguro que desea cancelar y salir?",
        "settings.title": "Ajustes",
        "settings.lang": "Idioma:",
        "cat.photos": "Fotos",
        "cat.iso": "ISO",
        "cat.docs": "Documentos",
        "cat.id": "Identificación",
        "cat.screen": "Pantalla",
        "cat.video": "Video",
        "cat.social": "Redes",
        "file_filter.images": "Imágenes",
        "file_filter.all": "Todos los archivos",
        "preset.letter": "Carta (8.5×11\")",
        "preset.legal": "Legal (8.5×14\")",
        "preset.tabloid": "Tabloide (11×17\")",
        "preset.id": "Carnet (32×43 mm)",
        "preset.passport": "Pasaporte (51×51 mm)",
        "preset.photo_4x6": "4 × 6\" (10×15 cm)",
        "preset.photo_5x7": "5 × 7\" (13×18 cm)",
        "preset.photo_6x8": "6 × 8\" (15×20 cm)",
        "preset.photo_8x10": "8 × 10\" (20×25 cm)",
        "preset.photo_11x14": "11 × 14\" (28×36 cm)",
        "preset.photo_12x16": "12 × 16\" (30×40 cm)",
        "preset.photo_16x20": "16 × 20\" (40×50 cm)",
        "preset.photo_24x36": "24 × 36\" (60×90 cm)",
        "preset.a3": "A3 (29.7×42 cm)",
        "preset.a4": "A4 (21×29.7 cm)",
        "preset.a5": "A5 (14.8×21 cm)",
        "preset.visa": "Visa (50×50 mm)",
        "preset.screen_720p": "HD 720p (1280×720)",
        "preset.screen_1080p": "Full HD 1080p (1920×1080)",
        "preset.screen_1440p": "WQHD 1440p (2560×1440)",
        "preset.screen_4k": "4K UHD (3840×2160)",
        "preset.video_480p": "SD 480p (854×480)",
        "preset.video_720p": "HD 720p (1280×720)",
        "preset.video_1080p": "Full HD 1080p (1920×1080)",
        "preset.video_2k": "2K DCI (2048×1080)",
        "preset.video_1440p": "QHD 1440p (2560×1440)",
        "preset.video_4k_uhd": "4K UHD (3840×2160)",
        "preset.video_4k_dci": "4K DCI (4096×2160)",
        "preset.video_8k": "8K UHD (7680×4320)",
        "preset.ig_square": "Instagram Cuadrado (1080×1080)",
        "preset.ig_landscape": "Instagram Horizontal (1080×566)",
        "preset.ig_portrait": "Instagram Vertical (1080×1350)",
        "preset.ig_stories": "Instagram Stories (1080×1920)",
        "preset.ig_profile": "Instagram Perfil (320×320)",
        "preset.fb_feed": "Facebook Feed (1200×630)",
        "preset.fb_cover": "Facebook Cover (820×312)",
        "preset.fb_stories": "Facebook Stories (1080×1920)",
        "preset.yt_thumbnail": "YouTube Thumbnail (1280×720)",
        "preset.yt_channel": "YouTube Canal (2560×1440)",
        "preset.yt_shorts": "YouTube Shorts (1080×1920)",
        "preset.tiktok": "TikTok/Reels (1080×1920)",
        "preset.twitter": "Twitter/X Post (1600×900)",
        "preset.linkedin": "LinkedIn (1200×627)",
        "preset.pinterest": "Pinterest (1000×1500)"
    },
    "en": {
        "ui.title": "PycResizer",
        "ui.tab.basic": " Basic ",
        "ui.tab.advanced": " Advanced ",
        "ui.label.input": "Input Files",
        "ui.label.output": "Output Folder",
        "ui.label.params": "Parameters",
        "ui.label.preset": "Preset:",
        "ui.label.width": "Width:",
        "ui.label.height": "Height:",
        "ui.label.unit": "Unit:",
        "ui.label.mode": "Mode:",
        "ui.label.dpi": "DPI:",
        "ui.btn.start": "Start",
        "ui.btn.cancel": "Cancel",
        "ui.btn.open_output": "Open Output",
        "ui.btn.browse": "Browse",
        "ui.btn.add_file": "Files",
        "ui.btn.add_folder": "Folder",
        "ui.btn.remove": "Remove",
        "ui.btn.clear": "Clear",
        "ui.status.ready": "Ready",
        "ui.status.processing": "{current} / {total} - {file}",
        "ui.status.cancelling": "Cancelling...",
        "ui.status.done": "Finished. OK: {ok}, Failed: {fail}",
        "ui.mode.fit": "Fit",
        "ui.mode.stretch": "Stretch",
        "ui.mode.fill": "Fill",
        "ui.mode.crop": "Crop",
        "err.empty_dpi": "DPI cannot be empty",
        "err.invalid_dpi": "DPI must be greater than zero",
        "err.invalid_dpi_type": "DPI must be numeric",
        "err.no_files": "No files",
        "err.no_files_msg": "No files selected. Add files or a folder.",
        "err.validation": "Validation Error",
        "err.missing_dims": "At least one dimension must be specified",
        "err.io_error": "Error processing image: {error}",
        "err.unexpected": "Unexpected error: {error}",
        "err.empty_value": "{field} cannot be empty",
        "err.not_numeric": "{field} must be numeric",
        "err.non_positive": "{field} must be greater than zero",
        "err.invalid_unit": "Invalid unit: {unit}",
        "err.invalid_input_dir": "Invalid input directory: {path}",
        "err.file_not_found": "File does not exist: {path}",
        "err.unsupported_format": "Unsupported format: {ext}",
        "err.invalid_dimensions": "Dimensions must be greater than zero",
        "err.negative_value": "Value cannot be negative",
        "err.conversion_failed": "Error converting {value}{unit}: {error}",
        "err.unsupported_unit": "Conversion not implemented: {unit}",
        "err.negative_pixels": "Pixels cannot be negative",
        "err.dir_not_found": "Directory does not exist: {dir}",
        "err.process_cancelled": "Process cancelled",
        "msg.done_success": "Processing finished. {ok} files processed successfully.",
        "msg.done_warning": "Processing finished with warnings. OK: {ok}, Failed: {fail}",
        "msg.done_title": "Completed",
        "msg.done_warn_title": "Completed with Warnings",
        "msg.error_title": "Error",
        "msg.warning_title": "Warning",
        "msg.cant_create_dir": "Could not create output directory: {error}",
        "msg.invalid_out_dir": "Output path is not a valid directory:\n{path}",
        "msg.cant_open_dir": "Cannot automatically open the file explorer on this system.\n\nPath: {path}",
        "msg.no_program_dir": "No program found to open folders.\n\nPath: {path}",
        "msg.permission_denied": "Permission denied to access:\n{path}",
        "msg.sys_error_dir": "System error when opening folder:\n{error}",
        "msg.close_confirm": "A process is currently running. Are you sure you want to cancel and exit?",
        "settings.title": "Settings",
        "settings.lang": "Language:",
        "cat.photos": "Photos",
        "cat.iso": "ISO",
        "cat.docs": "Documents",
        "cat.id": "ID Cards",
        "cat.screen": "Display",
        "cat.video": "Video",
        "cat.social": "Social Media",
        "file_filter.images": "Images",
        "file_filter.all": "All files",
        "preset.letter": "Letter (8.5×11\")",
        "preset.legal": "Legal (8.5×14\")",
        "preset.tabloid": "Tabloid (11×17\")",
        "preset.id": "ID Card (32×43 mm)",
        "preset.passport": "Passport (51×51 mm)",
        "preset.photo_4x6": "4 × 6\" (10×15 cm)",
        "preset.photo_5x7": "5 × 7\" (13×18 cm)",
        "preset.photo_6x8": "6 × 8\" (15×20 cm)",
        "preset.photo_8x10": "8 × 10\" (20×25 cm)",
        "preset.photo_11x14": "11 × 14\" (28×36 cm)",
        "preset.photo_12x16": "12 × 16\" (30×40 cm)",
        "preset.photo_16x20": "16 × 20\" (40×50 cm)",
        "preset.photo_24x36": "24 × 36\" (60×90 cm)",
        "preset.a3": "A3 (29.7×42 cm)",
        "preset.a4": "A4 (21×29.7 cm)",
        "preset.a5": "A5 (14.8×21 cm)",
        "preset.visa": "Visa (50×50 mm)",
        "preset.screen_720p": "HD 720p (1280×720)",
        "preset.screen_1080p": "Full HD 1080p (1920×1080)",
        "preset.screen_1440p": "WQHD 1440p (2560×1440)",
        "preset.screen_4k": "4K UHD (3840×2160)",
        "preset.video_480p": "SD 480p (854×480)",
        "preset.video_720p": "HD 720p (1280×720)",
        "preset.video_1080p": "Full HD 1080p (1920×1080)",
        "preset.video_2k": "2K DCI (2048×1080)",
        "preset.video_1440p": "QHD 1440p (2560×1440)",
        "preset.video_4k_uhd": "4K UHD (3840×2160)",
        "preset.video_4k_dci": "4K DCI (4096×2160)",
        "preset.video_8k": "8K UHD (7680×4320)",
        "preset.ig_square": "Instagram Square (1080×1080)",
        "preset.ig_landscape": "Instagram Landscape (1080×566)",
        "preset.ig_portrait": "Instagram Portrait (1080×1350)",
        "preset.ig_stories": "Instagram Stories (1080×1920)",
        "preset.ig_profile": "Instagram Profile (320×320)",
        "preset.fb_feed": "Facebook Feed (1200×630)",
        "preset.fb_cover": "Facebook Cover (820×312)",
        "preset.fb_stories": "Facebook Stories (1080×1920)",
        "preset.yt_thumbnail": "YouTube Thumbnail (1280×720)",
        "preset.yt_channel": "YouTube Channel (2560×1440)",
        "preset.yt_shorts": "YouTube Shorts (1080×1920)",
        "preset.tiktok": "TikTok/Reels (1080×1920)",
        "preset.twitter": "Twitter/X Post (1600×900)",
        "preset.linkedin": "LinkedIn (1200×627)",
        "preset.pinterest": "Pinterest (1000×1500)"
    }
}

class Translator:
    """Motor de traducción reactivo (Singleton)."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._current_lang = "es"
            cls._instance._observers: List[Callable] = []
            cls._instance._dicts = _TRANSLATIONS
        return cls._instance

    def set_language(self, lang_code: str):
        if lang_code in self._dicts:
            self._current_lang = lang_code
            self._notify_observers()

    def get(self, key: str, **kwargs) -> str:
        text = self._dicts[self._current_lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def add_observer(self, callback: Callable):
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: Callable):
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        dead_observers = []
        for callback in self._observers:
            # Introspección inteligente: si el callback pertenece a un widget Tkinter destruido, lo descartamos
            if hasattr(callback, '__self__') and hasattr(callback.__self__, 'winfo_exists'):
                try:
                    if not callback.__self__.winfo_exists():
                        dead_observers.append(callback)
                        continue
                except Exception:
                    dead_observers.append(callback)
                    continue

            try:
                callback()
            except tk.TclError as e:
                # Respaldo robusto para Tkinter TclError
                if "bad window" in str(e).lower() or "invalid command" in str(e).lower():
                    dead_observers.append(callback)
            except Exception:
                pass # Previene que un error aislado rompa la cadena de notificaciones

        # Limpieza reactiva para evitar Memory Leaks y referencias huérfanas
        for callback in dead_observers:
            if callback in self._observers:
                self._observers.remove(callback)

    @property
    def current_lang(self) -> str:
        return self._current_lang

tr = Translator()
