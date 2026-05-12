"""Tests for image resizing modes."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from PIL import Image
import tempfile

from src.core.image_processor import ImageProcessor, ResizeMode


def create_test_image(width, height, color=(255, 0, 0)):
    """Create a test image."""
    img = Image.new("RGB", (width, height), color)
    return img


def test_calculate_dimensions():
    """Validate calculated dimensions for each supported mode."""
    original_size = (800, 600)  # ratio 4:3
    target_size = (400, 400)    # square 1:1

    processor = ImageProcessor(dpi=300)

    assert processor._calculate_dimensions(original_size, *target_size, ResizeMode.STRETCH) == (400, 400)
    assert processor._calculate_dimensions(original_size, *target_size, ResizeMode.FIT) == (400, 300)
    assert processor._calculate_dimensions(original_size, *target_size, ResizeMode.FILL) == (400, 400)
    assert processor._calculate_dimensions(original_size, *target_size, ResizeMode.CROP) == (400, 400)


def test_apply_resize_visual():
    """Validate output image sizes for each supported mode."""
    original = (800, 600)  # landscape 4:3
    target = (400, 400)     # square 1:1

    processor = ImageProcessor(dpi=300)

    with tempfile.TemporaryDirectory():
        expected_sizes = {
            "STRETCH": (400, 400),
            "FIT": (400, 300),
            "FILL": (400, 400),
            "CROP": (400, 400),
        }
        for mode_name, mode in [
            ("STRETCH", ResizeMode.STRETCH),
            ("FIT", ResizeMode.FIT),
            ("FILL", ResizeMode.FILL),
            ("CROP", ResizeMode.CROP),
        ]:
            img = create_test_image(original[0], original[1])
            final_size = processor._calculate_dimensions(original, target[0], target[1], mode)
            processed = processor._apply_resize(img, final_size, mode, Image.Resampling.LANCZOS, (255, 255, 255))

            assert processed.size == expected_sizes[mode_name]


def test_ratio_edge_cases():
    """Validate resize calculations for extreme aspect ratios."""
    test_cases = [
        ((800, 600), (400, 400), "Landscape -> Square"),
        ((600, 800), (400, 400), "Portrait -> Square"),
        ((1000, 500), (400, 400), "Wide -> Square"),
        ((500, 1000), (400, 400), "Tall -> Square"),
        ((800, 600), (800, 600), "Same size"),
        ((800, 600), (1600, 1200), "Double size"),
    ]

    processor = ImageProcessor(dpi=300)

    for original, target, _desc in test_cases:
        for _mode_name, mode in [
            ("STRETCH", ResizeMode.STRETCH),
            ("FIT", ResizeMode.FIT),
            ("FILL", ResizeMode.FILL),
            ("CROP", ResizeMode.CROP),
        ]:
            result = processor._calculate_dimensions(original, target[0], target[1], mode)
            assert result[0] > 0
            assert result[1] > 0


if __name__ == "__main__":
    test_calculate_dimensions()
    test_apply_resize_visual()
    test_ratio_edge_cases()
