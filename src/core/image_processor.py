"""Procesamiento de imagenes individuales."""

from enum import Enum, auto
from pathlib import Path
from typing import Tuple, Union

from PIL import Image

from ..utils import (
    DEFAULT_DPI,
    SUPPORTED_EXTENSIONS,
    ProcessingError,
    ValidationError,
)
from .unit_converter import UnitConverter

Numeric = Union[int, float]


class ResizeMode(Enum):
    """Modos de redimensionamiento."""
    STRETCH = auto()
    FIT = auto()
    FILL = auto()
    CROP = auto()


class ImageProcessor:
    """Procesador de imagenes."""

    def __init__(self, dpi: int = DEFAULT_DPI, quality: int = 95):
        self.dpi = dpi
        self.quality = quality
        self._converter = UnitConverter()

    def resize(
        self,
        input_path: Path,
        output_path: Path,
        width: Numeric,
        height: Numeric,
        width_unit: str = "px",
        height_unit: str = "px",
        mode: ResizeMode = ResizeMode.FIT,
        resample: int = Image.Resampling.LANCZOS,
        background: Tuple[int, int, int, int] = (255, 255, 255, 255),
    ) -> Tuple[int, int]:
        """Redimensiona una imagen."""
        if not input_path.exists():
            raise ValidationError(f"Archivo no existe: {input_path}", code="FILE_NOT_FOUND")

        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValidationError(
                f"Formato no soportado: {input_path.suffix}",
                code="UNSUPPORTED_FORMAT"
            )

        try:
            with Image.open(input_path) as img:
                original_size = img.size
                target_width_px, target_height_px = self._resolve_dimensions(
                    img, width, height, width_unit, height_unit, self.dpi
                )

                if target_width_px <= 0 or target_height_px <= 0:
                    raise ValidationError(
                        "Dimensiones deben ser mayores que cero",
                        code="INVALID_DIMENSIONS"
                    )

                final_size = self._calculate_dimensions(
                    original_size, target_width_px, target_height_px, mode
                )

                processed = self._apply_resize(img, final_size, mode, resample, background)

                self._save_image(processed, output_path, self.dpi)

                return final_size

        except (OSError, IOError) as e:
            raise ProcessingError(f"Error al procesar imagen: {str(e)}", code="IO_ERROR")
        except ValidationError:
            raise
        except Exception as e:
            raise ProcessingError(f"Error inesperado: {str(e)}", code="UNEXPECTED_ERROR")

    def _resolve_dimensions(
        self,
        img: Image.Image,
        width: Numeric,
        height: Numeric,
        width_unit: str,
        height_unit: str,
        dpi: int,
    ) -> Tuple[int, int]:
        """Resuelve las dimensiones en pixeles."""
        width_provided = width is not None and width > 0
        height_provided = height is not None and height > 0

        if width_provided and height_provided:
            w_px = self._converter.to_pixels(width, width_unit, dpi)
            h_px = self._converter.to_pixels(height, height_unit, dpi)
            return (w_px, h_px)

        orig_w, orig_h = img.size
        orig_ratio = orig_w / orig_h

        if width_provided and not height_provided:
            w_px = self._converter.to_pixels(width, width_unit, dpi)
            h_px = int(w_px / orig_ratio)
            return (w_px, h_px)

        if height_provided and not width_provided:
            h_px = self._converter.to_pixels(height, height_unit, dpi)
            w_px = int(h_px * orig_ratio)
            return (w_px, h_px)

        raise ValidationError(
            "Debe especificar al menos una dimension",
            code="MISSING_DIMENSIONS"
        )

    def _calculate_dimensions(
        self,
        original_size: Tuple[int, int],
        target_width: int,
        target_height: int,
        mode: ResizeMode,
    ) -> Tuple[int, int]:
        """Calcula las dimensiones finales segun el modo."""
        orig_w, orig_h = original_size
        orig_ratio = orig_w / orig_h
        target_ratio = target_width / target_height

        if mode == ResizeMode.STRETCH:
            return (target_width, target_height)

        elif mode == ResizeMode.FIT:
            if target_ratio > orig_ratio:
                new_h = min(target_height, int(target_width / orig_ratio))
                new_w = int(new_h * orig_ratio)
            else:
                new_w = min(target_width, int(target_height * orig_ratio))
                new_h = int(new_w / orig_ratio)
            return (new_w, new_h)

        elif mode == ResizeMode.FILL:
            return (target_width, target_height)

        elif mode == ResizeMode.CROP:
            if target_ratio > orig_ratio:
                new_h = target_height
                new_w = int(new_h * orig_ratio)
                if new_w < target_width:
                    new_w = target_width
            else:
                new_w = target_width
                new_h = int(new_w / orig_ratio)
                if new_h < target_height:
                    new_h = target_height
            return (new_w, new_h)

        return (target_width, target_height)

    def _apply_resize(
        self,
        img: Image.Image,
        size: Tuple[int, int],
        mode: ResizeMode,
        resample: int,
        background: Tuple[int, int, int, int],
    ) -> Image.Image:
        """Aplica el redimensionamiento."""
        if mode == ResizeMode.FILL:
            img.thumbnail(size, resample)
            canvas = Image.new(img.mode, size, background[:3] if img.mode == "RGB" else background)
            offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
            canvas.paste(img, offset)
            return canvas

        if mode == ResizeMode.CROP:
            target_w, target_h = size
            
            orig_ratio = img.size[0] / img.size[1]
            target_ratio = target_w / target_h
            
            if orig_ratio > target_ratio:
                new_h = target_h
                new_w = int(new_h * orig_ratio)
            else:
                new_w = target_w
                new_h = int(new_w / orig_ratio)
            
            img = img.resize((new_w, new_h), resample)
            
            if img.size[0] > target_w:
                left = (img.size[0] - target_w) // 2
                img = img.crop((left, 0, left + target_w, target_h))
            
            if img.size[1] > target_h:
                top = (img.size[1] - target_h) // 2
                img = img.crop((0, top, target_w, top + target_h))
            
            return img

        return img.resize(size, resample)

    def _save_image(
        self,
        img: Image.Image,
        output_path: Path,
        dpi: int,
    ) -> None:
        """Guarda la imagen procesada."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}

        if output_path.suffix.lower() in (".jpg", ".jpeg"):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            save_kwargs["quality"] = self.quality
            save_kwargs["optimize"] = True
        elif output_path.suffix.lower() == ".png":
            save_kwargs["optimize"] = True

        dpi_to_save = (dpi, dpi)
        img.save(output_path, dpi=dpi_to_save, **save_kwargs)
