"""Conversion de unidades a pixeles."""

from typing import Union
from PIL import Image

from ..utils import DEFAULT_DPI, VALID_UNITS, ConversionError, ValidationError

Numeric = Union[int, float]


class UnitConverter:
    """Convierte unidades fisicas a pixeles."""

    @staticmethod
    def to_pixels(value: Numeric, unit: str, dpi: int = DEFAULT_DPI) -> int:
        """Convierte un valor a pixeles."""
        if unit not in VALID_UNITS:
            raise ValidationError(
                f"Unidad '{unit}' no valida. Use: {', '.join(VALID_UNITS)}",
                code="INVALID_UNIT"
            )

        if value < 0:
            raise ValidationError("El valor no puede ser negativo", code="NEGATIVE_VALUE")

        if dpi <= 0:
            raise ValidationError("DPI debe ser mayor que cero", code="INVALID_DPI")

        try:
            if unit == "px":
                return int(value)
            elif unit == "in":
                return int(value * dpi)
            elif unit == "cm":
                return int((value / 2.54) * dpi)
            elif unit == "mm":
                return int((value / 25.4) * dpi)
        except (TypeError, ValueError) as e:
            raise ConversionError(f"Error al convertir {value}{unit}: {str(e)}", code="CONVERSION_FAILED")

        raise ConversionError(f"Conversion no implementada: {unit}", code="UNSUPPORTED_UNIT")

    @staticmethod
    def from_pixels(pixels: int, unit: str, dpi: int = DEFAULT_DPI) -> float:
        """Convierte pixeles a una unidad."""
        if unit not in VALID_UNITS:
            raise ValidationError(f"Unidad '{unit}' no valida", code="INVALID_UNIT")
        
        if pixels < 0:
            raise ValidationError("Los pixeles no pueden ser negativos", code="NEGATIVE_PIXELS")
        
        if dpi <= 0:
            raise ValidationError("DPI debe ser mayor que cero", code="INVALID_DPI")
        
        if unit == "px":
            return float(pixels)
        elif unit == "in":
            return pixels / dpi
        elif unit == "cm":
            return (pixels / dpi) * 2.54
        elif unit == "mm":
            return (pixels / dpi) * 25.4
        
        raise ConversionError(f"Conversion no implementada: {unit}", code="UNSUPPORTED_UNIT")

    @staticmethod
    def get_image_dpi(image: Image.Image) -> int:
        """Extrae el DPI de una imagen."""
        if "dpi" in image.info and image.info["dpi"]:
            dpi = image.info["dpi"]
            if isinstance(dpi, tuple):
                return int(dpi[0])
            return int(dpi)
        return DEFAULT_DPI
