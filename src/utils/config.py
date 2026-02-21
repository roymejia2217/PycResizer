"""Configuracion central y constantes."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_DPI: int = 300
SUPPORTED_FORMATS: Tuple[str, ...] = ("PNG", "JPEG", "JPG", "BMP", "TIFF", "WEBP", "GIF")
SUPPORTED_EXTENSIONS: Tuple[str, ...] = tuple(f".{ext.lower()}" for ext in SUPPORTED_FORMATS)

UNIT_CONVERSIONS: Dict[str, float] = {
    "px": 1.0,
    "cm": 1.0,
    "mm": 0.1,
    "in": 2.54,
}

VALID_UNITS: Tuple[str, ...] = ("px", "cm", "mm", "in")

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
    name: str
    width: float
    height: float
    unit: str
    category: str
    keywords: List[str] = field(default_factory=list)


SIZE_PRESETS: List[SizePreset] = [
    SizePreset("4 × 6\" (10×15 cm)", 4, 6, "in", "Fotos", ["4x6", "10x15", "foto", "polaroid"]),
    SizePreset("5 × 7\" (13×18 cm)", 5, 7, "in", "Fotos", ["5x7", "13x18", "retrato"]),
    SizePreset("6 × 8\" (15×20 cm)", 6, 8, "in", "Fotos", ["6x8", "15x20", "marco"]),
    SizePreset("8 × 10\" (20×25 cm)", 8, 10, "in", "Fotos", ["8x10", "20x25", "profesional"]),
    SizePreset("11 × 14\" (28×36 cm)", 11, 14, "in", "Fotos", ["11x14", "28x36", "galeria"]),
    SizePreset("12 × 16\" (30×40 cm)", 12, 16, "in", "Fotos", ["12x16", "30x40", "arte"]),
    SizePreset("16 × 20\" (40×50 cm)", 16, 20, "in", "Fotos", ["16x20", "40x50", "poster"]),
    SizePreset("24 × 36\" (60×90 cm)", 24, 36, "in", "Fotos", ["24x36", "60x90", "gran formato"]),
    SizePreset("A3 (29.7×42 cm)", 29.7, 42, "cm", "ISO", ["a3", "iso", "dibujo"]),
    SizePreset("A4 (21×29.7 cm)", 21, 29.7, "cm", "ISO", ["a4", "iso", "documento", "oficina"]),
    SizePreset("A5 (14.8×21 cm)", 14.8, 21, "cm", "ISO", ["a5", "iso", "tarjeta", "folleto"]),
    SizePreset("Carta (8.5×11\")", 8.5, 11, "in", "Documentos", ["carta", "letter", "oficio"]),
    SizePreset("Legal (8.5×14\")", 8.5, 14, "in", "Documentos", ["legal", "contrato"]),
    SizePreset("Tabloide (11×17\")", 11, 17, "in", "Documentos", ["tabloide", "periódico"]),
    SizePreset("Carnet (32×43 mm)", 32, 43, "mm", "Identificación", ["carnet", "id", "cedula", "chile"]),
    SizePreset("Pasaporte (51×51 mm)", 51, 51, "mm", "Identificación", ["pasaporte", "visa"]),
    SizePreset("Visa (50×50 mm)", 50, 50, "mm", "Identificación", ["visa"]),
    SizePreset("HD 720p (1280×720)", 1280, 720, "px", "Pantalla", ["720p", "hd", "pantalla", "notebook"]),
    SizePreset("Full HD 1080p (1920×1080)", 1920, 1080, "px", "Pantalla", ["1080p", "full hd", "fhd", "escritorio", "monitor"]),
    SizePreset("WQHD 1440p (2560×1440)", 2560, 1440, "px", "Pantalla", ["1440p", "wqhd", "qhd", "2k"]),
    SizePreset("4K UHD (3840×2160)", 3840, 2160, "px", "Pantalla", ["4k", "uhd", "3840", "2160"]),
    SizePreset("SD 480p (854×480)", 854, 480, "px", "Video", ["480p", "sd", "streaming"]),
    SizePreset("HD 720p (1280×720)", 1280, 720, "px", "Video", ["720p", "hd", "broadcast"]),
    SizePreset("Full HD 1080p (1920×1080)", 1920, 1080, "px", "Video", ["1080p", "full hd", "youtube"]),
    SizePreset("2K DCI (2048×1080)", 2048, 1080, "px", "Video", ["2k", "dci", "cine"]),
    SizePreset("QHD 1440p (2560×1440)", 2560, 1440, "px", "Video", ["1440p", "qhd", "gaming"]),
    SizePreset("4K UHD (3840×2160)", 3840, 2160, "px", "Video", ["4k", "uhd", "netflix"]),
    SizePreset("4K DCI (4096×2160)", 4096, 2160, "px", "Video", ["4k", "dci", "cine digital"]),
    SizePreset("8K UHD (7680×4320)", 7680, 4320, "px", "Video", ["8k", "uhd"]),
    SizePreset("Instagram Cuadrado (1080×1080)", 1080, 1080, "px", "Redes", ["instagram", "fb", "feed", "1:1"]),
    SizePreset("Instagram Horizontal (1080×566)", 1080, 566, "px", "Redes", ["instagram", "horizontal"]),
    SizePreset("Instagram Vertical (1080×1350)", 1080, 1350, "px", "Redes", ["instagram", "vertical", "4:5"]),
    SizePreset("Instagram Stories (1080×1920)", 1080, 1920, "px", "Redes", ["stories", "reels", "tiktok", "9:16", "instagram"]),
    SizePreset("Instagram Perfil (320×320)", 320, 320, "px", "Redes", ["perfil", "avatar"]),
    SizePreset("Facebook Feed (1200×630)", 1200, 630, "px", "Redes", ["facebook", "feed", "publicacion"]),
    SizePreset("Facebook Cover (820×312)", 820, 312, "px", "Redes", ["facebook", "cover", "portada"]),
    SizePreset("Facebook Stories (1080×1920)", 1080, 1920, "px", "Redes", ["facebook", "stories"]),
    SizePreset("YouTube Thumbnail (1280×720)", 1280, 720, "px", "Redes", ["youtube", "thumbnail", "miniatura"]),
    SizePreset("YouTube Canal (2560×1440)", 2560, 1440, "px", "Redes", ["youtube", "banner", "canal"]),
    SizePreset("YouTube Shorts (1080×1920)", 1080, 1920, "px", "Redes", ["youtube", "shorts", "vertical"]),
    SizePreset("TikTok/Reels (1080×1920)", 1080, 1920, "px", "Redes", ["tiktok", "reels", "shorts", "vertical"]),
    SizePreset("Twitter/X Post (1600×900)", 1600, 900, "px", "Redes", ["twitter", "x", "post"]),
    SizePreset("LinkedIn (1200×627)", 1200, 627, "px", "Redes", ["linkedin", "profesional"]),
    SizePreset("Pinterest (1000×1500)", 1000, 1500, "px", "Redes", ["pinterest", "pin", "2:3"]),
]


def get_preset_categories() -> List[str]:
    """Obtiene categorías únicas de presets."""
    return sorted(set(p.category for p in SIZE_PRESETS))


def get_presets_by_category(category: str) -> List[SizePreset]:
    """Obtiene presets de una categoría específica."""
    return [p for p in SIZE_PRESETS if p.category == category]


def get_all_preset_names() -> List[str]:
    """Obtiene todos los nombres de presets."""
    return [p.name for p in SIZE_PRESETS]


def get_preset_by_name(name: str) -> SizePreset:
    """Obtiene un preset por nombre."""
    for preset in SIZE_PRESETS:
        if preset.name == name:
            return preset
    return SIZE_PRESETS[0]


def search_presets(query: str) -> List[SizePreset]:
    """Busca presets por nombre o keywords."""
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
