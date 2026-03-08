import sys
import os
import unittest
import tempfile
from pathlib import Path
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageChops
from src.core.image_processor import ImageProcessor, ResizeMode
from src.core.batch_handler import BatchHandler
from src.utils import ProcessingError


class TestCoreResilience(unittest.TestCase):
    """Pruebas de resiliencia de datos, manejo de errores y escrituras atomicas."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_dir = Path(self.temp_dir.name) / "input"
        self.output_dir = Path(self.temp_dir.name) / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        self.processor = ImageProcessor(dpi=300)
        self.handler = BatchHandler(processor=self.processor, max_workers=1)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_test_image(self, filename="test.jpg", color=(255, 0, 0), exif=b"fake_exif", icc=b"fake_icc"):
        filepath = self.input_dir / filename
        img = Image.new("RGB", (800, 600), color)
        
        info = {}
        if exif:
            info["exif"] = exif
        if icc:
            info["icc_profile"] = icc
            
        img.save(filepath, "JPEG", **info)
        return filepath

    def test_atomic_write_success(self):
        """Verifica que el guardado normal funcione y reemplace el archivo temporal."""
        img_path = self._create_test_image()
        out_path = self.output_dir / "out.jpg"

        final_size = self.processor.resize(
            input_path=img_path,
            output_path=out_path,
            width=400,
            height=300,
            mode=ResizeMode.FIT
        )

        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 0)
        
        # Verificar que no hay temporales basura en la carpeta
        tmps = list(self.output_dir.glob(".tmp_*"))
        self.assertEqual(len(tmps), 0)

    def test_atomic_write_failure_cleanup(self):
        """Simula fallo en el guardado (ej. disco lleno) para asegurar que no queden archivos 0 bytes."""
        img_path = self._create_test_image()
        out_path = self.output_dir / "out.jpg"

        # Mockear el save de PIL para que falle
        original_save = Image.Image.save
        
        def fake_save(*args, **kwargs):
            # Simulamos crear un archivo a medio terminar y luego fallar
            tmp_path = args[1] if len(args) > 1 else kwargs.get("fp")
            if isinstance(tmp_path, (str, Path)):
                with open(tmp_path, "w") as f:
                    f.write("incompleto")
            raise OSError("Disco lleno simulado")

        Image.Image.save = fake_save

        try:
            with self.assertRaises(ProcessingError) as context:
                self.processor.resize(
                    input_path=img_path,
                    output_path=out_path,
                    width=400,
                    height=300,
                    mode=ResizeMode.FIT
                )
            
            self.assertIn("Disco lleno simulado", str(context.exception))
            
            # El archivo final no debe existir (sin corrupción)
            self.assertFalse(out_path.exists())
            
            # El archivo temporal debe haber sido limpiado
            tmps = list(self.output_dir.glob(".tmp_*"))
            self.assertEqual(len(tmps), 0)
        finally:
            Image.Image.save = original_save

    def test_file_collision_prevention(self):
        """Prueba que evite sobreescribir el archivo de entrada directamente."""
        img_path = self._create_test_image("collide.jpg")
        
        # Usamos mismo directorio de entrada como salida, y sin sufijo
        results = self.handler.process_batch(
            input_files=[img_path],
            output_dir=self.input_dir,  # Mismo dir!
            width=400,
            height=300,
            width_unit="px",
            height_unit="px",
            mode=ResizeMode.FIT,
            suffix=""  # Sin sufijo!
        )
        
        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertTrue(res.success)
        
        # El nombre debió cambiar para evitar colision
        self.assertEqual(res.output_path.name, "collide_pyc.jpg")
        self.assertTrue(res.output_path.exists())
        self.assertTrue(img_path.exists()) # El original sigue intacto

    def test_cancel_early_abort(self):
        """Verifica que al cancelar, el proceso aborte tempranamente sin guardar archivos."""
        img_path = self._create_test_image()
        out_path = self.output_dir / "cancelled.jpg"

        def mock_cancel_check():
            return True # Simula que el usuario ya clickeo cancelar

        with self.assertRaises(ProcessingError) as context:
            self.processor.resize(
                input_path=img_path,
                output_path=out_path,
                width=400,
                height=300,
                mode=ResizeMode.FIT,
                cancel_check=mock_cancel_check
            )

        self.assertEqual(context.exception.code, "CANCELLED")
        self.assertFalse(out_path.exists())

    def test_batch_cancel_signal(self):
        """Verifica que el manejador batch intercepte y pase la señal de cancelación."""
        img_path1 = self._create_test_image("img1.jpg")
        img_path2 = self._create_test_image("img2.jpg")
        
        results = []
        
        def run_batch():
            nonlocal results
            results = self.handler.process_batch(
                input_files=[img_path1, img_path2],
                output_dir=self.output_dir,
                width=400,
                height=300,
                width_unit="px",
                height_unit="px",
                mode=ResizeMode.FIT,
                suffix="_out"
            )

        t = threading.Thread(target=run_batch)
        t.start()
        
        # Simulamos que el usuario da click en cancelar rapidísimo
        time.sleep(0.01)
        self.handler.cancel()
        t.join()
        
        self.assertEqual(len(results), 2)
        # Al menos 1 debe haber fallado por cancelación (el thread principal es suficientemente rapido para matar el segundo en un entorno mock)
        # o ambos fallan si la cancelacion entra antes del loop
        has_cancelled = any(not r.success and "cancel" in r.error_message.lower() for r in results)
        self.assertTrue(has_cancelled, "Se esperaba que al menos un archivo reportara cancelación.")

    def test_metadata_retention(self):
        """Verifica la retención de perfiles ICC y datos EXIF."""
        import piexif
        
        # Crear un EXIF basico y real con piexif para el test
        exif_dict = {"0th": {piexif.ImageIFD.Make: b"TestCamera"}, "Exif": {}, "GPS": {}, "1st": {}, "Interop": {}}
        fake_exif = piexif.dump(exif_dict)
        fake_icc = b"FakeICCProfileData"
        
        img_path = self._create_test_image(exif=fake_exif, icc=fake_icc)
        out_path = self.output_dir / "meta_out.jpg"
        
        self.processor.resize(
            input_path=img_path,
            output_path=out_path,
            width=400,
            height=300,
            mode=ResizeMode.FIT
        )
        
        # Leemos la salida y validamos
        with Image.open(out_path) as img_out:
            self.assertIn("icc_profile", img_out.info, "Deberia conservar el perfil ICC")
            self.assertEqual(img_out.info.get("icc_profile"), fake_icc)
            self.assertIn("exif", img_out.info, "Deberia conservar los metadatos EXIF")
            
            # Verificamos que piexif pueda leerlo y la metadata siga ahi
            out_exif_dict = piexif.load(img_out.info.get("exif"))
            self.assertEqual(out_exif_dict["0th"].get(piexif.ImageIFD.Make), b"TestCamera")

    def test_directory_validation(self):
        """Verifica que la prueba estática de permisos de directorio funcione."""
        # Directorio valido
        self.assertTrue(BatchHandler.validate_output_directory(self.output_dir))
        
        # Crear un archivo e intentar usarlo como directorio (deberia fallar limpia)
        fake_dir = Path(self.temp_dir.name) / "archivo.txt"
        with open(fake_dir, "w") as f:
            f.write("no soy directorio")
            
        self.assertFalse(BatchHandler.validate_output_directory(fake_dir))


if __name__ == "__main__":
    unittest.main()
