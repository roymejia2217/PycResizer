"""Tests for unit conversion behavior."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from src.core.unit_converter import UnitConverter
from src.utils import DEFAULT_DPI


def test_conversion_logic():
    """Validate round-trip unit conversion with pixel rounding tolerance."""
    print("=" * 60)
    print("TEST: Unit conversion")
    print("=" * 60)
    
    dpi = 300
    
    test_cases = [
        {"from": ("cm", 21, 29.7), "to": "mm", "expected": (210.0, 297.0)},
        {"from": ("cm", 21, 29.7), "to": "in", "expected": (8.2677, 11.6929)},
        {"from": ("cm", 21, 29.7), "to": "px", "expected": (2480, 3508)},
        {"from": ("in", 8.5, 11), "to": "cm", "expected": (21.59, 27.94)},
        {"from": ("mm", 210, 297), "to": "cm", "expected": (21.0, 29.7)},
        {"from": ("px", 2480, 3508), "to": "cm", "expected": (21.0, 29.7)},
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        from_unit, from_w, from_h = test["from"]
        to_unit = test["to"]
        expected_w, expected_h = test["expected"]
        
        w_px = UnitConverter.to_pixels(from_w, from_unit, dpi)
        h_px = UnitConverter.to_pixels(from_h, from_unit, dpi)
        
        result_w = UnitConverter.from_pixels(w_px, to_unit, dpi)
        result_h = UnitConverter.from_pixels(h_px, to_unit, dpi)
        
        tolerance = 0.1 if to_unit != "px" else 1
        passed = (
            abs(result_w - expected_w) <= tolerance and 
            abs(result_h - expected_h) <= tolerance
        )
        
        status = "✓ PASS" if passed else "✗ FAIL"
        all_passed = all_passed and passed
        
        print(f"\nTest {i}: {from_w}{from_unit} x {from_h}{from_unit} -> {to_unit}")
        print(f"  Expected: {expected_w:.2f} x {expected_h:.2f}")
        print(f"  Got:      {result_w:.2f} x {result_h:.2f}")
        print(f"  Status:   {status}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
    
    assert all_passed


def test_unit_converter_functions():
    """Exercise UnitConverter functions with representative values."""
    print("\n" + "=" * 60)
    print("TEST: UnitConverter functions")
    print("=" * 60)
    
    dpi = 300
    
    print("\n1. to_pixels(21, 'cm', 300):")
    try:
        result = UnitConverter.to_pixels(21, "cm", dpi)
        print(f"   Result: {result}")
        print(f"   Expected: 2480")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n2. to_pixels(29.7, 'cm', 300):")
    try:
        result = UnitConverter.to_pixels(29.7, "cm", dpi)
        print(f"   Result: {result}")
        print(f"   Expected: 3508")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n3. from_pixels(2480, 'cm', 300):")
    try:
        result = UnitConverter.from_pixels(2480, "cm", dpi)
        print(f"   Result: {result}")
        print(f"   Expected: ~21.0")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n4. from_pixels(2480, 'mm', 300):")
    try:
        result = UnitConverter.from_pixels(2480, "mm", dpi)
        print(f"   Result: {result}")
        print(f"   Expected: ~210.0")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n5. from_pixels(2480, 'in', 300):")
    try:
        result = UnitConverter.from_pixels(2480, "in", dpi)
        print(f"   Result: {result}")
        print(f"   Expected: ~8.27")
    except Exception as e:
        print(f"   ERROR: {e}")


def test_gui_binding():
    """Smoke test GUI binding setup when a display is available."""
    print("\n" + "=" * 60)
    print("TEST: GUI binding verification")
    print("=" * 60)
    
    try:
        import tkinter as tk
        import ttkbootstrap as tb
        
        root = tk.Tk()
        root.withdraw()
        
        window = tb.Window(themename="darkly")
        window.withdraw()
        
        window._build_ui()
        
        print("\nChecking that widgets exist...")
        
        checks = [
            ("preset_var", hasattr(window, 'preset_var')),
            ("preset_cb", hasattr(window, 'preset_cb')),
            ("width_entry", hasattr(window, 'width_entry')),
            ("height_entry", hasattr(window, 'height_entry')),
            ("unit_var", hasattr(window, 'unit_var')),
            ("unit_cb", hasattr(window, 'unit_cb')),
            ("dpi_var", hasattr(window, 'dpi_var')),
            ("dpi_entry", hasattr(window, 'dpi_entry')),
            ("mode_var", hasattr(window, 'mode_var')),
            ("mode_cb", hasattr(window, 'mode_cb')),
            ("_chain_var", hasattr(window, '_chain_var')),
        ]
        
        all_ok = True
        for name, exists in checks:
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {exists}")
            all_ok = all_ok and exists
        
        print(f"\nChecking bound events...")
        
        if hasattr(window, 'preset_cb'):
            bindings = window.preset_cb.bind()
            print(f"  preset_cb bindings: {bindings}")
        
        if hasattr(window, 'unit_cb'):
            bindings = window.unit_cb.bind()
            print(f"  unit_cb bindings: {bindings}")
        
        root.destroy()
        
        if all_ok:
            print("\n✓ GUI configured correctly")
        else:
            print("\n✗ Some widgets are missing")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_conversion_logic()
    test_unit_converter_functions()
    test_gui_binding()
