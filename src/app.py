"""Punto de entrada de la aplicacion."""

from pathlib import Path
import sys

src_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(src_dir.parent))

from src.gui.main_window import run

if __name__ == "__main__":
    run()
