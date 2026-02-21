"""Test para el caso de uso de Recortar (CROP) a tamanos pequenos como carnet."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from PIL import Image
import tempfile

from src.core.image_processor import ImageProcessor, ResizeMode


def create_test_image_centered(width, height, center_color=(255, 0, 0), border_color=(0, 255, 0)):
    """Crea una imagen con marca visible en el centro."""
    img = Image.new("RGB", (width, height), border_color)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    center_w, center_h = width // 4, height // 4
    draw.ellipse(
        [center_w, center_h, width - center_w, height - center_h],
        fill=center_color
    )
    return img


def test_crop_to_id_card():
    """Test: Redimensionar imagen grande a tamanio de carnet."""
    print("=" * 70)
    print("TEST: Recortar a tamanio de carnet (32x43mm = 377x507px @ 300 DPI)")
    print("=" * 70)
    
    dpi = 300
    processor = ImageProcessor(dpi=dpi)
    
    from src.core.unit_converter import UnitConverter
    
    card_width_mm = 32
    card_height_mm = 43
    
    card_width_px = UnitConverter.to_pixels(card_width_mm, "mm", dpi)
    card_height_px = UnitConverter.to_pixels(card_height_mm, "mm", dpi)
    
    print(f"\nTarget carnet: {card_width_mm}x{card_height_mm}mm = {card_width_px}x{card_height_px}px @ {dpi} DPI")
    
    test_images = [
        (3000, 4000, "Vertical 3:4 (tipica foto celular)"),
        (4000, 3000, "Horizontal 4:3 (tipica foto celular)"),
        (1920, 1080, "HD 16:9"),
        (3840, 2160, "4K 16:9"),
        (1600, 1200, "Compacta 4:3"),
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for orig_w, orig_h, desc in test_images:
            print(f"\n{'-'*70}")
            print(f"Imagen original: {orig_w}x{orig_h} ({desc})")
            print(f"Ratio original: {orig_w/orig_h:.3f}")
            print(f"Ratio target:   {card_width_px/card_height_px:.3f}")
            
            target_w = card_width_px
            target_h = card_height_px
            
            final_size = processor._calculate_dimensions(
                (orig_w, orig_h), 
                target_w, 
                target_h, 
                ResizeMode.CROP
            )
            print(f"\n  Dimension calculada: {final_size}")
            
            img = create_test_image_centered(orig_w, orig_h)
            
            processed = processor._apply_resize(
                img, 
                final_size, 
                ResizeMode.CROP, 
                Image.Resampling.LANCZOS,
                (255, 255, 255)
            )
            
            print(f"  Imagen resultado:  {processed.size}")
            
            expected_ratio = target_w / target_h
            actual_ratio = processed.size[0] / processed.size[1]
            ratio_match = abs(expected_ratio - actual_ratio) < 0.01
            print(f"  Ratio esperado: {expected_ratio:.3f}")
            print(f"  Ratio actual:   {actual_ratio:.3f}")
            print(f"  Ratio coincide: {'SI' if ratio_match else 'NO'}")
            
            output_path = Path(tmpdir) / f"crop_{orig_w}x{orig_h}.png"
            processed.save(output_path)
            print(f"  Guardado: {output_path.name}")


def test_crop_center_position():
    """Test para verificar que el crop es desde el centro."""
    print("\n" + "=" * 70)
    print("TEST: Verificar que el crop es desde el centro")
    print("=" * 70)
    
    processor = ImageProcessor(dpi=300)
    
    original = (1000, 1000)
    target = (300, 400)
    
    print(f"\nOriginal: {original}")
    print(f"Target:   {target}")
    
    final_size = processor._calculate_dimensions(original, target[0], target[1], ResizeMode.CROP)
    print(f"Calculada: {final_size}")
    
    img = create_test_image_centered(original[0], original[1], center_color=(255, 0, 0))
    
    processed = processor._apply_resize(
        img, 
        final_size, 
        ResizeMode.CROP, 
        Image.Resampling.LANCZOS,
        (255, 255, 255)
    )
    
    print(f"Resultado: {processed.size}")
    
    from PIL import ImageDraw
    draw = ImageDraw.Draw(processed)
    
    center_color = processed.getpixel((processed.width // 2, processed.height // 2))
    print(f"Color en centro: {center_color}")
    
    is_centered = center_color == (255, 0, 0) or center_color == (254, 0, 0)
    print(f"Centro mantiene color rojo (-centered): {'SI' if is_centered else 'NO'}")


def test_crop_edge_cases():
    """Test de casos extremos para crop."""
    print("\n" + "=" * 70)
    print("TEST: Casos extremos para CROP")
    print("=" * 70)
    
    processor = ImageProcessor(dpi=300)
    
    cases = [
        ((3000, 4000), (377, 507), "Foto vertical -> Carnet"),
        ((4000, 3000), (377, 507), "Foto horizontal -> Carnet"),
        ((1080, 1920), (377, 507), "Celular vertical -> Carnet"),
        ((500, 500), (1000, 1000), "Imagen pequena -> Grande"),
        ((1000, 500), (500, 1000), "Horizontal->Vertical"),
        ((500, 1000), (1000, 500), "Vertical->Horizontal"),
    ]
    
    for (orig_w, orig_h), (target_w, target_h), desc in cases:
        final_size = processor._calculate_dimensions(
            (orig_w, orig_h), 
            target_w, 
            target_h, 
            ResizeMode.CROP
        )
        
        expected_ratio = target_w / target_h
        actual_ratio = final_size[0] / final_size[1] if final_size[1] > 0 else 0
        
        print(f"\n{desc}")
        print(f"  {orig_w}x{orig_h} -> {final_size} (target: {target_w}x{target_h})")
        print(f"  Ratio target: {expected_ratio:.3f}, Ratio result: {actual_ratio:.3f}")


if __name__ == "__main__":
    test_crop_to_id_card()
    test_crop_center_position()
    test_crop_edge_cases()
