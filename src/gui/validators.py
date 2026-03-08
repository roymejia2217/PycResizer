"""Validadores de entrada para la GUI."""

from pathlib import Path
from typing import Optional, Tuple, Union

from ..utils import VALID_UNITS, ValidationError
from ..utils.i18n import tr


def parse_positive_float(value: str, field_key: str) -> float:
    """Convierte texto a float positivo."""
    value = value.strip()
    if not value:
        raise ValidationError(tr.get("err.empty_value", field=tr.get(field_key)), code="EMPTY_VALUE")
    try:
        number = float(value)
    except ValueError:
        raise ValidationError(tr.get("err.not_numeric", field=tr.get(field_key)), code="NOT_NUMERIC")
    if number <= 0:
        raise ValidationError(tr.get("err.non_positive", field=tr.get(field_key)), code="NON_POSITIVE")
    return number


def parse_optional_positive_float(value: str, field_key: str) -> Optional[float]:
    """Convierte texto a float positivo o devuelve None."""
    value = value.strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        raise ValidationError(f"{tr.get(field_key)}: {tr.get('err.invalid_dpi')}", code="NOT_NUMERIC")
    if number <= 0:
        raise ValidationError(f"{tr.get(field_key)}: {tr.get('err.invalid_dpi')}", code="NON_POSITIVE")
    return number


def validate_unit(unit: str) -> str:
    """Valida que la unidad sea soportada."""
    unit = unit.strip().lower()
    if unit not in VALID_UNITS:
        raise ValidationError(
            f"Invalid unit: {unit}. Use: {', '.join(VALID_UNITS)}",
            code="INVALID_UNIT",
        )
    return unit


def validate_directories(input_dir: str, output_dir: str) -> Tuple[Path, Path]:
    """Valida directorios de entrada y salida."""
    input_path: Path = Path(input_dir).expanduser() if input_dir else Path("")
    output_path = Path(output_dir).expanduser()

    if input_dir and (not input_path.exists() or not input_path.is_dir()):
        raise ValidationError(
            f"Invalid input directory: {input_path}",
            code="INVALID_INPUT_DIR",
        )

    return input_path, output_path
