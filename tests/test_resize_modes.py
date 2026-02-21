"""Test para verificar los modos de redimensionamiento."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from PIL import Image
import tempfile

from src.core.image_processor import ImageProcessor, ResizeMode


def create_test_image(width, height, color=(255, 0, 0)):
    """Crea una imagen de prueba."""
    img = Image.new("RGB", (width, height), color)
    return img


def test_calculate_dimensions():
    """Test de calculo de dimensiones por modo."""
    print("=" * 70)
    print("TEST: Calculo de dimensiones por modo")
    print("=" * 70)
    
    original_size = (800, 600)  # ratio 4:3
    target_size = (400, 400)    # square 1:1
    
    print(f"\nImagen original: {original_size[0]}x{original_size[1]} (ratio: {original_size[0]/original_size[1]:.3f})")
    print(f"Target esperado:  {target_size[0]}x{target_size[1]} (ratio: {target_size[0]/target_size[1]:.3f})")
    print("-" * 70)
    
    processor = ImageProcessor(dpi=300)
    
    modes = [
        ("STRETCH", ResizeMode.STRETCH),
        ("MAINTAIN_ASPECT", ResizeMode.MAINTAIN_ASPECT),
        ("FIT", ResizeMode.FIT),
        ("FILL", ResizeMode.FILL),
    ]
    
    results = {}
    for name, mode in modes:
        result = processor._calculate_dimensions(original_size, target_size[0], target_size[1], mode)
        results[name] = result
        print(f"{name:20s}: {result[0]:4d} x {result[1]:4d}  (ratio: {result[0]/result[1]:.3f})")
    
    print("\n" + "=" * 70)
    print("ANALISIS:")
    print("=" * 70)
    
    # Comparar resultados
    print(f"\n1. STRETCH: {results['STRETCH']}")
    print(f"   -> Fuerza las dimensiones exactas (puede deformar)")
    
    print(f"\n2. MAINTAIN_ASPECT: {results['MAINTAIN_ASPECT']}")
    print(f"   -> Mantiene aspecto, dimensiones Calculadas segun ratio original")
    
    print(f"\n3. FIT: {results['FIT']}")
    print(f"   -> Ajusta para Caber dentro del target (similar a MAINTAIN_ASPECT)")
    
    print(f"\n4. FILL: {results['FILL']}")
    print(f"   -> Llena el target completamente (puede recorte)")
    
    # Verificar si hay redundancias
    print("\n" + "=" * 70)
    print("REDUNDANCIAS DETECTADAS:")
    print("=" * 70)
    
    if results['STRETCH'] == (400, 400):
        print("- STRETCH y FILL dan el mismo resultado en _calculate_dimensions")
        print("  (FILL hace el trabajo extra en _apply_resize con thumbnail+canvas)")
    
    if results['MAINTAIN_ASPECT'] == results['FIT']:
        print("- MAINTAIN_ASPECT y FIT dan el mismo resultado")
        print("  (La diferencia real esta en el manejo de casos edge)")
    
    return results


def test_apply_resize_visual():
    """Test visual de como cada modo afecta la imagen."""
    print("\n" + "=" * 70)
    print("TEST: Comportamiento visual de cada modo")
    print("=" * 70)
    
    original = (800, 600)  # landscape 4:3
    target = (400, 400)     # square 1:1
    
    print(f"\nOriginal: {original[0]}x{original[1]} -> Target: {target[0]}x{target[1]}")
    print("-" * 70)
    
    processor = ImageProcessor(dpi=300)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for mode_name, mode in [
            ("STRETCH", ResizeMode.STRETCH),
            ("MAINTAIN_ASPECT", ResizeMode.MAINTAIN_ASPECT),
            ("FIT", ResizeMode.FIT),
            ("FILL", ResizeMode.FILL),
        ]:
            img = create_test_image(original[0], original[1])
            
            final_size = processor._calculate_dimensions(original, target[0], target[1], mode)
            
            processed = processor._apply_resize(img, final_size, mode, Image.Resampling.LANCZOS, (255, 255, 255))
            
            print(f"\n{mode_name}:")
            print(f"  - Dimension calculada: {final_size}")
            print(f"  - Imagen resultado:   {processed.size}")
            
            if mode == ResizeMode.FILL:
                print(f"  - Comportamiento: Rellena con fondo blanco y centra la imagen")
            elif mode == ResizeMode.STRETCH:
                print(f"  - Comportamiento: Deforma a exacto 400x400")
            elif mode == ResizeMode.MAINTAIN_ASPECT:
                print(f"  - Comportamiento: Mantiene 4:3, resultado {final_size}")
            elif mode == ResizeMode.FIT:
                print(f"  - Comportamiento: Ajusta para Caber, resultado {final_size}")


def test_ratio_edge_cases():
    """Test con casos extremos de proporciones."""
    print("\n" + "=" * 70)
    print("TEST: Casos extremos de proporciones")
    print("=" * 70)
    
    test_cases = [
        ((800, 600), (400, 400), "Landscape -> Square"),
        ((600, 800), (400, 400), "Portrait -> Square"),
        ((1000, 500), (400, 400), "Wide -> Square"),
        ((500, 1000), (400, 400), "Tall -> Square"),
        ((800, 600), (800, 600), "Same size"),
        ((800, 600), (1600, 1200), "Double size"),
    ]
    
    processor = ImageProcessor(dpi=300)
    
    for original, target, desc in test_cases:
        print(f"\n{desc}")
        print(f"  Original: {original[0]}x{original[1]} (ratio: {original[0]/original[1]:.3f})")
        print(f"  Target:  {target[0]}x{target[1]} (ratio: {target[0]/target[1]:.3f})")
        
        for mode_name, mode in [
            ("STRETCH", ResizeMode.STRETCH),
            ("MAINTAIN", ResizeMode.MAINTAIN_ASPECT),
            ("FIT", ResizeMode.FIT),
            ("FILL", ResizeMode.FILL),
        ]:
            result = processor._calculate_dimensions(original, target[0], target[1], mode)
            print(f"    {mode_name:12s}: {result[0]:4d} x {result[1]:4d}")


def suggest_modes():
    """Sugiere consolidacion de modos."""
    print("\n" + "=" * 70)
    print("SUGERENCIAS DE CONSOLIDACION")
    print("=" * 70)
    
    print("""
MODOS ACTUALES Y SU PROPOSITO:

1. STRETCH - Forzar dimensiones exactas (deforma si es necesario)
   Uso: Cuando quieres exactamente 400x400 sin importar proporciones

2. MAINTAIN_ASPECT - Mantener proporción original
   Uso: Imagen proportionally ms pequeña, puede no llenar el rea

3. FIT - Ajustar para Caber
   Uso: Imagen que cabe completamente dentro del rea objetivo

4. FILL - Llenar con fondo
   Uso: Imagen que llena el rea, se recorta si es ms grande

ANALISIS:
- STRETCH = FILL en _calculate_dimensions, diferente en _apply_resize
- MAINTAIN_ASPECT y FIT son muy similares (diferencia es min() en FIT)

MODO FALTANTE:
- CROP: Recortar la imagen para llenar exactamente el rea objetivo
  (sin fondo, slo recorte - lo opuesto a FILL)

MODOS RECOMENDADOS PARA LA GUI:
1. Estirar (STRETCH) - Forzar dimensiones
2. Ajustar (FIT) - Mantener aspecto,缩 smaller
3. Rellenar (FILL) - Llenar con fondo
4. Recortar (CROP) - Recortar sin fondo  <-- NUEVO
""")


if __name__ == "__main__":
    test_calculate_dimensions()
    test_apply_resize_visual()
    test_ratio_edge_cases()
    suggest_modes()
