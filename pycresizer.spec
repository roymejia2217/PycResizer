# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for PycResizer."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


block_cipher = None

project_root = Path(SPECPATH)
assets_dir = project_root / "assets"
icon_file = assets_dir / "icon.ico"

datas_list = []

if icon_file.exists():
    datas_list.append((str(icon_file), "assets"))
    print(f"[INFO] Application icon found: {icon_file}")
else:
    print(f"[WARN] Application icon not found: {icon_file}")

try:
    icon_data_files = collect_data_files("ttkbootstrap_icons_bs", includes=["assets/*"])
    if icon_data_files:
        datas_list.extend(icon_data_files)
        print(f"[INFO] Bootstrap icon assets collected: {len(icon_data_files)} entries")
    else:
        print("[WARN] No Bootstrap icon assets were collected")
except Exception as exc:
    print(f"[WARN] Bootstrap icon assets could not be collected: {exc}")

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
        "PIL._tkinter_finder",
        "piexif",
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
    icon=str(icon_file) if icon_file.exists() else None,
)
