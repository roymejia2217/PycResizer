"""Test de rendimiento para procesamiento batch."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from typing import List, Tuple
import random

from src.core.batch_handler import BatchHandler, ProcessingResult
from src.core.image_processor import ImageProcessor, ResizeMode
from src.utils import DEFAULT_DPI


def create_test_images(directory: Path, count: int, size_range: Tuple[int, int], color_variation: bool = True):
    """Crea imagenes de prueba de diferentes tamanos."""
    print(f"  Creando {count} imagenes de prueba...")
    
    min_size, max_size = size_range
    sizes = [
        (800, 600),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160),
        (1024, 768),
        (1600, 1200),
        (3000, 2000),
    ]
    
    files = []
    for i in range(count):
        size = random.choice(sizes)
        
        if color_variation:
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
            color = (r, g, b)
        else:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        img = Image.new("RGB", size, color)
        
        filename = f"test_image_{i:04d}.jpg"
        filepath = directory / filename
        img.save(filepath, "JPEG", quality=85)
        files.append(filepath)
    
    print(f"  Creadas {len(files)} imagenes")
    return files


def test_single_thread_vs_multiworker():
    """Compara rendimiento single-thread vs multi-worker."""
    print("\n" + "=" * 70)
    print("TEST: Single-thread vs Multi-worker")
    print("=" * 70)
    
    image_counts = [10, 50, 100]
    worker_counts = [1, 2, 4, 8]
    
    results_summary = {}
    
    for img_count in image_counts:
        print(f"\n--- {img_count} imagenes ---")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            input_dir = tmppath / "input"
            output_dir = tmppath / "output"
            input_dir.mkdir()
            output_dir.mkdir()
            
            create_test_images(input_dir, img_count, (800, 3840))
            
            files = list(input_dir.glob("*.jpg"))
            
            for workers in worker_counts:
                processor = ImageProcessor(dpi=300)
                handler = BatchHandler(processor=processor, max_workers=workers)
                
                start = time.perf_counter()
                results = handler.process_batch(
                    input_files=files,
                    output_dir=output_dir,
                    width=800,
                    height=600,
                    width_unit="px",
                    height_unit="px",
                    mode=ResizeMode.FIT,
                )
                elapsed = time.perf_counter() - start
                
                success_count = sum(1 for r in results if r.success)
                throughput = img_count / elapsed if elapsed > 0 else 0
                
                key = f"{img_count}_{workers}"
                results_summary[key] = {
                    "images": img_count,
                    "workers": workers,
                    "time": elapsed,
                    "success": success_count,
                    "throughput": throughput
                }
                
                print(f"  {workers} workers: {elapsed:.2f}s ({throughput:.1f} img/s)")
    
    print("\n" + "=" * 70)
    print("RESUMEN:")
    print("=" * 70)
    print(f"{'Imagenes':<12} {'Workers':<10} {'Tiempo':<10} {'Throughput':<15}")
    print("-" * 50)
    for key, data in sorted(results_summary.items()):
        print(f"{data['images']:<12} {data['workers']:<10} {data['time']:<10.2f} {data['throughput']:<15.1f}")


def test_different_modes():
    """Prueba rendimiento con diferentes modos de redimensionamiento."""
    print("\n" + "=" * 70)
    print("TEST: Diferentes modos de redimensionamiento")
    print("=" * 70)
    
    img_count = 50
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        input_dir = tmppath / "input"
        output_dir = tmppath / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        create_test_images(input_dir, img_count, (1920, 3840))
        files = list(input_dir.glob("*.jpg"))
        
        modes = [
            ("FIT", ResizeMode.FIT),
            ("STRETCH", ResizeMode.STRETCH),
            ("FILL", ResizeMode.FILL),
            ("CROP", ResizeMode.CROP),
        ]
        
        for mode_name, mode in modes:
            processor = ImageProcessor(dpi=300)
            handler = BatchHandler(processor=processor, max_workers=4)
            
            start = time.perf_counter()
            results = handler.process_batch(
                input_files=files,
                output_dir=output_dir,
                width=800,
                height=600,
                width_unit="px",
                height_unit="px",
                mode=mode,
            )
            elapsed = time.perf_counter() - start
            
            success_count = sum(1 for r in results if r.success)
            throughput = img_count / elapsed
            
            print(f"  {mode_name}: {elapsed:.2f}s ({throughput:.1f} img/s) - OK: {success_count}/{img_count}")


def test_different_presets():
    """Prueba rendimiento con diferentes presets."""
    print("\n" + "=" * 70)
    print("TEST: Diferentes presets/tamanos objetivo")
    print("=" * 70)
    
    from src.utils import get_all_preset_names, get_preset_by_name
    
    presets_to_test = [
        "A5 (14.8×21 cm)",
        "A4 (21×29.7 cm)",
        "8 × 10\" (20×25 cm)",
        "4 × 6\" (10×15 cm)",
        "Carnet (32×43 mm)",
    ]
    
    img_count = 30
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        for preset_name in presets_to_test:
            input_dir = tmppath / "input"
            output_dir = tmppath / "output"
            input_dir.mkdir(exist_ok=True)
            output_dir.mkdir(exist_ok=True)
            
            create_test_images(input_dir, img_count, (1920, 3840))
            files = list(input_dir.glob("*.jpg"))
            
            preset = get_preset_by_name(preset_name)
            
            processor = ImageProcessor(dpi=300)
            handler = BatchHandler(processor=processor, max_workers=4)
            
            start = time.perf_counter()
            results = handler.process_batch(
                input_files=files,
                output_dir=output_dir,
                width=preset.width,
                height=preset.height,
                width_unit=preset.unit,
                height_unit=preset.unit,
                mode=ResizeMode.FIT,
            )
            elapsed = time.perf_counter() - start
            
            success_count = sum(1 for r in results if r.success)
            throughput = img_count / elapsed
            
            print(f"  {preset_name}: {elapsed:.2f}s ({throughput:.1f} img/s)")
            
            for f in files:
                f.unlink()


def test_memory_usage():
    """Analiza uso de memoria durante procesamiento."""
    print("\n" + "=" * 70)
    print("TEST: Uso de memoria")
    print("=" * 70)
    
    try:
        import psutil
        process = psutil.Process()
    except ImportError:
        print("  psutil no instalado, saltando test de memoria")
        return
    
    img_count = 100
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        input_dir = tmppath / "input"
        output_dir = tmppath / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        create_test_images(input_dir, img_count, (1920, 1080))
        files = list(input_dir.glob("*.jpg"))
        
        mem_before = process.memory_info().rss / 1024 / 1024
        print(f"  Memoria antes: {mem_before:.1f} MB")
        
        processor = ImageProcessor(dpi=300)
        handler = BatchHandler(processor=processor, max_workers=4)
        
        results = handler.process_batch(
            input_files=files,
            output_dir=output_dir,
            width=1920,
            height=1080,
            width_unit="px",
            height_unit="px",
            mode=ResizeMode.FIT,
        )
        
        mem_after = process.memory_info().rss / 1024 / 1024
        print(f"  Memoria despues: {mem_after:.1f} MB")
        print(f"  Diferencia: {mem_after - mem_before:.1f} MB")
        
        success_count = sum(1 for r in results if r.success)
        print(f"  Procesadas: {success_count}/{img_count}")


def test_error_handling():
    """Prueba manejo de errores durante procesamiento batch."""
    print("\n" + "=" * 70)
    print("TEST: Manejo de errores")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        input_dir = tmppath / "input"
        output_dir = tmppath / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        files = []
        
        valid_img = Image.new("RGB", (800, 600), (255, 0, 0))
        valid_img.save(input_dir / "valid1.jpg", "JPEG")
        files.append(input_dir / "valid1.jpg")
        
        valid_img.save(input_dir / "valid2.png", "PNG")
        files.append(input_dir / "valid2.png")
        
        corrupt_file = input_dir / "corrupt.jpg"
        with open(corrupt_file, "wb") as f:
            f.write(b"NOT AN IMAGE")
        files.append(corrupt_file)
        
        nonexistent = input_dir / "nonexistent.jpg"
        files.append(nonexistent)
        
        processor = ImageProcessor(dpi=300)
        handler = BatchHandler(processor=processor, max_workers=2)
        
        results = handler.process_batch(
            input_files=files,
            output_dir=output_dir,
            width=100,
            height=100,
            width_unit="px",
            height_unit="px",
            mode=ResizeMode.FIT,
        )
        
        print(f"  Total archivos: {len(files)}")
        for result in results:
            status = "OK" if result.success else "ERROR"
            print(f"    {result.input_path.name}: {status}")
            if not result.success:
                print(f"      -> {result.error_message[:80]}")


def test_optimal_workers():
    """Determina el numero optimo de workers."""
    print("\n" + "=" * 70)
    print("TEST: Determinacion de workers optimos")
    print("=" * 70)
    
    import multiprocessing
    
    cpu_count = multiprocessing.cpu_count()
    print(f"  CPUs disponibles: {cpu_count}")
    
    img_count = 100
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        input_dir = tmppath / "input"
        output_dir = tmppath / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        create_test_images(input_dir, img_count, (1920, 1080))
        files = list(input_dir.glob("*.jpg"))
        
        worker_range = range(1, min(cpu_count + 2, 9))
        
        best_time = float('inf')
        best_workers = 1
        
        for workers in worker_range:
            processor = ImageProcessor(dpi=300)
            handler = BatchHandler(processor=processor, max_workers=workers)
            
            for f in output_dir.glob("*"):
                f.unlink()
            
            start = time.perf_counter()
            results = handler.process_batch(
                input_files=files,
                output_dir=output_dir,
                width=800,
                height=600,
                width_unit="px",
                height_unit="px",
                mode=ResizeMode.FIT,
            )
            elapsed = time.perf_counter() - start
            
            throughput = img_count / elapsed
            
            marker = ""
            if elapsed < best_time:
                best_time = elapsed
                best_workers = workers
                marker = " *"
            
            print(f"  {workers} workers: {elapsed:.2f}s ({throughput:.1f} img/s){marker}")
        
        print(f"\n  Workers optimos: {best_workers}")


if __name__ == "__main__":
    print("=" * 70)
    print("SUITE DE TESTS DE RENDIMIENTO")
    print("=" * 70)
    
    test_single_thread_vs_multiworker()
    test_different_modes()
    test_different_presets()
    test_optimal_workers()
    test_memory_usage()
    test_error_handling()
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETADOS")
    print("=" * 70)
