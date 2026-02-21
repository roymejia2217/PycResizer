"""Procesamiento por lotes de imagenes."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from PIL import Image

from ..utils import SUPPORTED_EXTENSIONS, FileSystemError
from .image_processor import ImageProcessor, ResizeMode
from ..utils.config import VALID_UNITS


def _get_optimal_workers() -> int:
    """Calcula el numero de workers segun nucleos de CPU."""
    try:
        cpu_count = os.cpu_count() or 4
        return min(cpu_count + 1, 8)
    except Exception:
        return 4


@dataclass
class ProcessingResult:
    """Resultado del procesamiento de una imagen."""
    input_path: Path
    output_path: Path
    success: bool
    original_size: Tuple[int, int]
    final_size: Tuple[int, int] = (0, 0)
    error_message: str = ""
    processing_time: float = 0.0


class BatchHandler:
    """Manejador de procesamiento por lotes."""

    def __init__(
        self,
        processor: ImageProcessor,
        max_workers: int = 0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        """Inicializa el manejador."""
        self._processor = processor
        self._max_workers = max_workers if max_workers > 0 else _get_optimal_workers()
        self._progress_callback = progress_callback
        self._lock = threading.Lock()
        self._cancelled = False

    def process_batch(
        self,
        input_files: List[Path],
        output_dir: Path,
        width: Optional[float],
        height: Optional[float],
        width_unit: str,
        height_unit: str,
        mode: ResizeMode,
        suffix: str = "_resized",
    ) -> List[ProcessingResult]:
        """Procesa un lote de imagenes."""
        self._cancelled = False
        results: List[ProcessingResult] = []
        total = len(input_files)
        processed = 0

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            return [
                ProcessingResult(
                    input_path=Path(""),
                    output_path=output_dir,
                    success=False,
                    original_size=(0, 0),
                    error_message=f"No se pudo crear directorio de salida: {str(e)}"
                )
            ]

        def process_single(file_path: Path) -> ProcessingResult:
            if self._cancelled:
                return ProcessingResult(
                    input_path=file_path,
                    output_path=Path(),
                    success=False,
                    original_size=(0, 0),
                    error_message="Proceso cancelado"
                )

            try:
                with Image.open(file_path) as img:
                    original_size = img.size

                output_name = f"{file_path.stem}{suffix}{file_path.suffix}"
                output_path = output_dir / output_name

                final_size = self._processor.resize(
                    input_path=file_path,
                    output_path=output_path,
                    width=width,
                    height=height,
                    width_unit=width_unit,
                    height_unit=height_unit,
                    mode=mode,
                )

                return ProcessingResult(
                    input_path=file_path,
                    output_path=output_path,
                    success=True,
                    original_size=original_size,
                    final_size=final_size,
                )

            except Exception as e:
                return ProcessingResult(
                    input_path=file_path,
                    output_path=output_dir / f"{file_path.stem}{suffix}{file_path.suffix}",
                    success=False,
                    original_size=(0, 0),
                    error_message=str(e),
                )

        def update_progress(result: ProcessingResult):
            nonlocal processed
            with self._lock:
                processed += 1
                if self._progress_callback:
                    self._progress_callback(processed, total, result.input_path.name)
            return result

        if self._max_workers == 1:
            for file_path in input_files:
                result = process_single(file_path)
                results.append(update_progress(result))
        else:
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                future_to_file = {
                    executor.submit(process_single, fp): fp for fp in input_files
                }
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(update_progress(result))

        return sorted(results, key=lambda r: str(r.input_path))

    def cancel(self):
        """Cancela el procesamiento en curso."""
        self._cancelled = True

    @staticmethod
    def scan_directory(directory: Path, recursive: bool = False) -> List[Path]:
        """Escanea un directorio buscando imagenes."""
        if not directory.exists():
            raise FileSystemError(f"Directorio no existe: {directory}", code="DIR_NOT_FOUND")

        files = []
        pattern = "**/*" if recursive else "*"

        for item in directory.glob(pattern):
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(item)

        return sorted(files)

    @staticmethod
    def validate_output_directory(directory: Path) -> bool:
        """Verifica que el directorio de salida sea escribible."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            test_file = directory / f".write_test_{id(directory)}"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except (OSError, PermissionError):
                return False
        except (OSError, PermissionError):
            return False
