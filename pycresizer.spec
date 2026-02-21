# -*- mode: python ; coding: utf-8 -*-
"""
Spec file para construir PycResizer con PyInstaller (onefile).
Ejecutar: pyinstaller pycresizer.spec --clean
"""

import os
import sys
from pathlib import Path

block_cipher = None

project_root = Path(SPECPATH)
assets_dir = project_root / "assets"
icon_file = assets_dir / "icon.ico"

icon_exists = icon_file.exists()

venv_path = Path(sys.prefix)
site_packages = venv_path / "Lib" / "site-packages"
ttkbootstrap_icons_bs_path = site_packages / "ttkbootstrap_icons_bs"

datas_list = []

if icon_exists:
    datas_list.append((str(icon_file), "assets"))
    print(f"[INFO] Icono de app encontrado: {icon_file}")

if ttkbootstrap_icons_bs_path.exists():
    assets_path = ttkbootstrap_icons_bs_path / "assets"
    if assets_path.exists():
        datas_list.append((str(assets_path), "ttkbootstrap_icons_bs/assets"))
        print(f"[INFO] Iconos BS encontrados: {assets_path}")
    else:
        print(f"[WARN] assets no encontrado en: {ttkbootstrap_icons_bs_path}")
else:
    print(f"[WARN] ttkbootstrap_icons_bs no encontrado en: {ttkbootstrap_icons_bs_path}")

a = Analysis(
    [str(project_root / "src" / "app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        "PIL",
        "PIL.Image",
        "PIL.ImageOps",
        "PIL.ImageDraw",
        "PIL.ImageFilter",
        "ttkbootstrap",
        "ttkbootstrap.themes",
        "ttkbootstrap.dialogs",
        "ttkbootstrap.constants",
        "ttkbootstrap_icons_bs",
        "ttkbootstrap_icons_bs.provider",
        "concurrent.futures",
        "concurrent.futures.thread",
        "threading",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "pytest",
        "IPython",
        "jupyter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PycResizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_exists else None,
    version_info={
        "Version": "1.0.0",
        "CompanyName": "PycResizer",
        "FileDescription": "Procesador de imágenes por lotes",
        "ProductName": "PycResizer",
    },
)
