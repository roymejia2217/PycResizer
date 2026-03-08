"""Tests para la arquitectura de presets y traducciones."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import (
    SIZE_PRESETS,
    VALID_UNITS,
    UNIT_CONVERSIONS,
    get_preset_by_name,
    get_all_preset_names,
)
from src.utils.i18n import tr

class TestPresetsArchitecture(unittest.TestCase):

    def test_dynamic_units(self):
        """Verifica que las unidades validas se deriven dinamicamente."""
        self.assertEqual(tuple(UNIT_CONVERSIONS.keys()), VALID_UNITS)

    def test_no_hardcoded_presets(self):
        """Asegura que todos los presets usen claves de internacionalizacion."""
        for preset in SIZE_PRESETS:
            self.assertTrue(
                preset.name_key.startswith("preset."), 
                f"Hardcoding detectado en preset: {preset.name_key}"
            )
            # Verificar que la clave exista en ambos idiomas
            tr.set_language("es")
            es_name = preset.name
            self.assertNotEqual(es_name, preset.name_key, f"Falta traduccion ES para: {preset.name_key}")
            
            tr.set_language("en")
            en_name = preset.name
            self.assertNotEqual(en_name, preset.name_key, f"Falta traduccion EN para: {preset.name_key}")

    def test_o1_cache_performance(self):
        """Verifica que la busqueda y cache reaccionen correctamente al cambio de idioma."""
        tr.set_language("es")
        es_names = get_all_preset_names()
        preset_es = get_preset_by_name(es_names[0])
        self.assertEqual(preset_es.name, es_names[0])
        
        # Test specific differing preset
        ig_es = get_preset_by_name("Instagram Cuadrado (1080×1080)")
        self.assertEqual(ig_es.width, 1080)

        tr.set_language("en")
        en_names = get_all_preset_names()
        preset_en = get_preset_by_name(en_names[0])
        self.assertEqual(preset_en.name, en_names[0])
        
        ig_en = get_preset_by_name("Instagram Square (1080×1080)")
        self.assertEqual(ig_en.width, 1080)
        self.assertEqual(ig_es, ig_en)

if __name__ == "__main__":
    unittest.main()
