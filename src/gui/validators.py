"""Validadores de entrada para la GUI."""

from pathlib import Path
from typing import Optional, Tuple, Union

from ..utils import VALID_UNITS, ValidationError


def parse_positive_float(value: str, field_name: str) -> float:
    """Convierte texto a float positivo."""
    value = value.strip()
    if not value:
        raise ValidationError(f"{field_name} no puede estar vacio", code="EMPTY_VALUE")
    try:
        number = float(value)
    except ValueError:
        raise ValidationError(f"{field_name} debe ser numerico", code="NOT_NUMERIC")
    if number <= 0:
        raise ValidationError(f"{field_name} debe ser mayor que cero", code="NON_POSITIVE")
    return number


def parse_optional_positive_float(value: str, field_name: str) -> Optional[float]:
    """Convierte texto a float positivo o devuelve None."""
    value = value.strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        raise ValidationError(f"{field_name} debe ser numerico", code="NOT_NUMERIC")
    if number <= 0:
        raise ValidationError(f"{field_name} debe ser mayor que cero", code="NON_POSITIVE")
    return number


def validate_unit(unit: str) -> str:
    """Valida que la unidad sea soportada."""
    unit = unit.strip().lower()
    if unit not in VALID_UNITS:
        raise ValidationError(
            f"Unidad no valida: {unit}. Use: {', '.join(VALID_UNITS)}",
            code="INVALID_UNIT",
        )
    return unit


def validate_directories(input_dir: str, output_dir: str) -> Tuple[Path, Path]:
    """Valida directorios de entrada y salida."""
    input_path: Path = Path(input_dir).expanduser() if input_dir else Path("")
    output_path = Path(output_dir).expanduser()

    if input_dir and (not input_path.exists() or not input_path.is_dir()):
        raise ValidationError(
            f"Directorio de entrada invalido: {input_path}",
            code="INVALID_INPUT_DIR",
        )

    return input_path, output_path
