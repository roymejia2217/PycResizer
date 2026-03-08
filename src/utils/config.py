"""Configuracion central y constantes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
from .i18n import tr

DEFAULT_DPI: int = 300
SUPPORTED_FORMATS: Tuple[str, ...] = ("PNG", "JPEG", "JPG", "BMP", "TIFF", "WEBP", "GIF")
SUPPORTED_EXTENSIONS: Tuple[str, ...] = tuple(f".{ext.lower()}" for ext in SUPPORTED_FORMATS)

UNIT_CONVERSIONS: Dict[str, float] = {
    "px": 1.0,
    "cm": 1.0,
    "mm": 0.1,
    "in": 2.54,
}

VALID_UNITS: Tuple[str, ...] = tuple(UNIT_CONVERSIONS.keys())

RESAMPLE_FILTERS = {
    "LANCZOS": "LANCZOS",
    "BICUBIC": "BICUBIC",
    "BILINEAR": "BILINEAR",
    "NEAREST": "NEAREST",
}

DEFAULT_OUTPUT_SUFFIX: str = "_resized"
DEFAULT_RESAMPLE: str = "LANCZOS"

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR: Path = Path.home() / "Downloads" / "PycResizer" / "output"


@dataclass
class SizePreset:
    """Preset de tamaño predefinido."""
    name_key: str
    width: float
    height: float
    unit: str
    category_key: str
    keywords: List[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        translated = tr.get(self.name_key)
        return translated if translated != self.name_key else self.name_key

    @property
    def category(self) -> str:
        return tr.get(self.category_key)


SIZE_PRESETS: List[SizePreset] = [
    SizePreset("preset.photo_4x6", 4, 6, "in", "cat.photos", ["4x6", "10x15", "foto", "polaroid"]),
    SizePreset("preset.photo_5x7", 5, 7, "in", "cat.photos", ["5x7", "13x18", "retrato"]),
    SizePreset("preset.photo_6x8", 6, 8, "in", "cat.photos", ["6x8", "15x20", "marco"]),
    SizePreset("preset.photo_8x10", 8, 10, "in", "cat.photos", ["8x10", "20x25", "profesional"]),
    SizePreset("preset.photo_11x14", 11, 14, "in", "cat.photos", ["11x14", "28x36", "galeria"]),
    SizePreset("preset.photo_12x16", 12, 16, "in", "cat.photos", ["12x16", "30x40", "arte"]),
    SizePreset("preset.photo_16x20", 16, 20, "in", "cat.photos", ["16x20", "40x50", "poster"]),
    SizePreset("preset.photo_24x36", 24, 36, "in", "cat.photos", ["24x36", "60x90", "gran formato"]),
    SizePreset("preset.a3", 29.7, 42, "cm", "cat.iso", ["a3", "iso", "dibujo"]),
    SizePreset("preset.a4", 21, 29.7, "cm", "cat.iso", ["a4", "iso", "documento", "oficina"]),
    SizePreset("preset.a5", 14.8, 21, "cm", "cat.iso", ["a5", "iso", "tarjeta", "folleto"]),
    SizePreset("preset.letter", 8.5, 11, "in", "cat.docs", ["carta", "letter", "oficio"]),
    SizePreset("preset.legal", 8.5, 14, "in", "cat.docs", ["legal", "contrato"]),
    SizePreset("preset.tabloid", 11, 17, "in", "cat.docs", ["tabloide", "periódico"]),
    SizePreset("preset.id", 32, 43, "mm", "cat.id", ["carnet", "id", "cedula", "chile"]),
    SizePreset("preset.passport", 51, 51, "mm", "cat.id", ["pasaporte", "visa"]),
    SizePreset("preset.visa", 50, 50, "mm", "cat.id", ["visa"]),
    SizePreset("preset.screen_720p", 1280, 720, "px", "cat.screen", ["720p", "hd", "pantalla", "notebook"]),
    SizePreset("preset.screen_1080p", 1920, 1080, "px", "cat.screen", ["1080p", "full hd", "fhd", "escritorio", "monitor"]),
    SizePreset("preset.screen_1440p", 2560, 1440, "px", "cat.screen", ["1440p", "wqhd", "qhd", "2k"]),
    SizePreset("preset.screen_4k", 3840, 2160, "px", "cat.screen", ["4k", "uhd", "3840", "2160"]),
    SizePreset("preset.video_480p", 854, 480, "px", "cat.video", ["480p", "sd", "streaming"]),
    SizePreset("preset.video_720p", 1280, 720, "px", "cat.video", ["720p", "hd", "broadcast"]),
    SizePreset("preset.video_1080p", 1920, 1080, "px", "cat.video", ["1080p", "full hd", "youtube"]),
    SizePreset("preset.video_2k", 2048, 1080, "px", "cat.video", ["2k", "dci", "cine"]),
    SizePreset("preset.video_1440p", 2560, 1440, "px", "cat.video", ["1440p", "qhd", "gaming"]),
    SizePreset("preset.video_4k_uhd", 3840, 2160, "px", "cat.video", ["4k", "uhd", "netflix"]),
    SizePreset("preset.video_4k_dci", 4096, 2160, "px", "cat.video", ["4k", "dci", "cine digital"]),
    SizePreset("preset.video_8k", 7680, 4320, "px", "cat.video", ["8k", "uhd"]),
    SizePreset("preset.ig_square", 1080, 1080, "px", "cat.social", ["instagram", "fb", "feed", "1:1"]),
    SizePreset("preset.ig_landscape", 1080, 566, "px", "cat.social", ["instagram", "horizontal"]),
    SizePreset("preset.ig_portrait", 1080, 1350, "px", "cat.social", ["instagram", "vertical", "4:5"]),
    SizePreset("preset.ig_stories", 1080, 1920, "px", "cat.social", ["stories", "reels", "tiktok", "9:16", "instagram"]),
    SizePreset("preset.ig_profile", 320, 320, "px", "cat.social", ["perfil", "avatar"]),
    SizePreset("preset.fb_feed", 1200, 630, "px", "cat.social", ["facebook", "feed", "publicacion"]),
    SizePreset("preset.fb_cover", 820, 312, "px", "cat.social", ["facebook", "cover", "portada"]),
    SizePreset("preset.fb_stories", 1080, 1920, "px", "cat.social", ["facebook", "stories"]),
    SizePreset("preset.yt_thumbnail", 1280, 720, "px", "cat.social", ["youtube", "thumbnail", "miniatura"]),
    SizePreset("preset.yt_channel", 2560, 1440, "px", "cat.social", ["youtube", "banner", "canal"]),
    SizePreset("preset.yt_shorts", 1080, 1920, "px", "cat.social", ["youtube", "shorts", "vertical"]),
    SizePreset("preset.tiktok", 1080, 1920, "px", "cat.social", ["tiktok", "reels", "shorts", "vertical"]),
    SizePreset("preset.twitter", 1600, 900, "px", "cat.social", ["twitter", "x", "post"]),
    SizePreset("preset.linkedin", 1200, 627, "px", "cat.social", ["linkedin", "profesional"]),
    SizePreset("preset.pinterest", 1000, 1500, "px", "cat.social", ["pinterest", "pin", "2:3"]),
]

_PRESET_CACHE_LANG = None
_NAME_TO_PRESET: Dict[str, SizePreset] = {}


def _build_preset_cache():
    """Genera una caché O(1) de los presets, reactiva al cambio de idioma."""
    global _PRESET_CACHE_LANG, _NAME_TO_PRESET
    if _PRESET_CACHE_LANG != tr.current_lang:
        _NAME_TO_PRESET = {p.name: p for p in SIZE_PRESETS}
        _PRESET_CACHE_LANG = tr.current_lang


def get_preset_categories() -> List[str]:
    """Obtiene categorías únicas de presets (traducidas)."""
    return sorted(set(p.category for p in SIZE_PRESETS))


def get_presets_by_category(category_name: str) -> List[SizePreset]:
    """Obtiene presets de una categoría específica (por nombre traducido)."""
    return [p for p in SIZE_PRESETS if p.category == category_name]


def get_all_preset_names() -> List[str]:
    """Obtiene todos los nombres de presets (traducidos) en O(1) vía caché."""
    _build_preset_cache()
    return list(_NAME_TO_PRESET.keys())


def get_preset_by_name(name: str) -> SizePreset:
    """Obtiene un preset por su nombre traducido utilizando caché O(1)."""
    _build_preset_cache()
    return _NAME_TO_PRESET.get(name, SIZE_PRESETS[0])


def search_presets(query: str) -> List[SizePreset]:
    """Busca presets por nombre traducido o keywords."""
    if not query or not query.strip():
        return SIZE_PRESETS
    
    query_lower = query.lower().strip()
    results = []
    
    for preset in SIZE_PRESETS:
        if query_lower in preset.name.lower():
            results.append(preset)
        elif any(query_lower in kw.lower() for kw in preset.keywords):
            results.append(preset)
    
    return results if results else SIZE_PRESETS


def search_preset_names(query: str) -> List[str]:
    """Busca nombres de presets por query."""
    results = search_presets(query)
    return [p.name for p in results]
