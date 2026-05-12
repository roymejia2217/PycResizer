<p align="center">
  <img src="docs/banner.webp" alt="PycResizer banner" width="900">
</p>

<p align="center">
  <img src="docs/logo.png" alt="PycResizer logo" width="128" height="128">
</p>

<h1 align="center">PycResizer</h1>

<p align="center">
  Batch image resizing for photos, documents, social media assets, and display formats.
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  </a>
  <a href="https://pypi.org/project/Pillow/">
    <img src="https://img.shields.io/badge/Pillow-12.1.1-orange.svg" alt="Pillow">
  </a>
  <a href="https://pypi.org/project/ttkbootstrap/">
    <img src="https://img.shields.io/badge/ttkbootstrap-1.20.1-purple.svg" alt="ttkbootstrap">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  </a>
  <a href="https://pyinstaller.org/">
    <img src="https://img.shields.io/badge/PyInstaller-6.19.0-red.svg" alt="PyInstaller">
  </a>
</p>

## Overview

PycResizer is a desktop batch image processor built with Python, Tkinter, ttkbootstrap, and Pillow. It resizes multiple images at once using manual dimensions, physical units, DPI conversion, and curated presets.

## Features

- Batch processing for PNG, JPEG, BMP, TIFF, WEBP, and GIF files.
- Presets for photos, ISO paper sizes, documents, ID cards, displays, video, and social media.
- Resize modes for fit, stretch, fill, and crop workflows.
- Unit conversion between pixels, centimeters, millimeters, and inches.
- DPI-aware output sizing for print-oriented formats.
- Parallel processing with cancellation support.
- English and Spanish interface translations inside the application.
- Automated Windows executable and Debian package builds from Git tags.

## Screenshots

### Main Interface

<p align="center">
  <img src="docs/screenshots/ui.webp" alt="PycResizer main interface" width="520">
</p>

### Presets

<p align="center">
  <img src="docs/screenshots/preset.webp" alt="PycResizer preset selector" width="520">
</p>

### Resize Modes

<p align="center">
  <img src="docs/screenshots/modo.webp" alt="PycResizer resize modes" width="520">
</p>

## Requirements

- Python 3.10 or newer.
- Tkinter support in the Python installation.
- Linux users need a desktop environment capable of running Tk applications.

## Run From Source

```bash
git clone <repository-url>
cd PycResizer
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src/app.py
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Build Locally

Create a PyInstaller build:

```bash
python -m pip install -r requirements.txt
pyinstaller pycresizer.spec --clean --noconfirm
```

Expected outputs:

- Windows: `dist/PycResizer.exe`
- Linux: `dist/PycResizer`

Create a Debian package after a Linux PyInstaller build:

```bash
scripts/build_deb.sh
```

The Debian package is written to `dist/packages/`.

## Release Builds

GitHub Actions builds release artifacts when a Git tag is pushed. The workflow uses one matrix for Windows and Linux:

- Windows builds a portable `.exe`.
- Linux builds a standalone executable archive and a Debian `.deb` package.
- The release job publishes all generated artifacts to the matching GitHub Release.

Example:

```bash
git tag v1.1.0
git push origin v1.1.0
```

## Project Structure

```text
PycResizer/
├── .github/workflows/        # Release automation
├── assets/                   # Runtime application icon
├── docs/                     # README banner, logo, and screenshots
│   └── screenshots/
├── packaging/linux/          # Linux desktop integration files
├── scripts/                  # Build and packaging scripts
├── src/
│   ├── app.py                # Application entry point
│   ├── core/                 # Image processing and batch logic
│   ├── gui/                  # Tkinter/ttkbootstrap interface
│   └── utils/                # Configuration, icons, i18n, and errors
├── tests/                    # Automated and validation tests
├── pycresizer.spec           # PyInstaller build specification
└── requirements.txt          # Pinned build/runtime dependencies
```

## License

PycResizer is released under the MIT License. See [LICENSE](LICENSE) for details.
