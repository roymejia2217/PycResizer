"""Static validation for release packaging and documentation files."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_uses_docs_assets_only():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "README_ES.md" not in readme
    assert "assets/pyc.png" not in readme
    assert "assets/ui.webp" not in readme
    assert "assets/preset.webp" not in readme
    assert "assets/modo.webp" not in readme

    for relative_path in [
        "docs/banner.webp",
        "docs/screenshots/ui.webp",
        "docs/screenshots/preset.webp",
        "docs/screenshots/modo.webp",
    ]:
        assert relative_path in readme
        assert (ROOT / relative_path).is_file()

    assert (ROOT / "docs/logo.png").is_file()


def test_release_workflow_is_tag_matrix_based():
    workflow_path = ROOT / ".github" / "workflows" / "build-release.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    assert "tags:" in workflow
    assert "windows-latest" in workflow
    assert "ubuntu-latest" in workflow
    assert "strategy:" in workflow
    assert "matrix:" in workflow
    assert "contents: write" in workflow
    assert "gh release create" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert workflow.count("actions/checkout@v4") >= 2
    assert "scripts/build_deb.sh" in workflow
    assert "dotnet tool install --global wix" in workflow
    assert "wix build" in workflow
    assert "-acceptEula wix7" in workflow
    assert "pycresizer-windows-${{ github.ref_name }}.zip" in workflow
    assert "pycresizer-windows-${{ github.ref_name }}.msi" in workflow
    assert "-pdbtype none" in workflow
    assert "Copy-Item -Path dist/PycResizer.exe" not in workflow


def test_pyinstaller_spec_includes_tk_image_bridge():
    spec_path = ROOT / "pycresizer.spec"
    spec = spec_path.read_text(encoding="utf-8")

    assert "PIL._tkinter_finder" in spec


def test_debian_packaging_script_has_required_controls():
    script_path = ROOT / "scripts" / "build_deb.sh"
    script = script_path.read_text(encoding="utf-8")

    assert "set -euo pipefail" in script
    assert "dpkg-deb --root-owner-group --build" in script
    assert "Package:" in script
    assert "Version:" in script
    assert "Architecture:" in script
    assert "usr/share/applications" in script
    assert "usr/share/icons/hicolor/256x256/apps" in script
    assert "opt/pycresizer" in script


def test_desktop_entry_matches_freedesktop_basics():
    desktop_path = ROOT / "packaging" / "linux" / "pycresizer.desktop"
    desktop = desktop_path.read_text(encoding="utf-8")

    assert "[Desktop Entry]" in desktop
    assert "Type=Application" in desktop
    assert "Name=PycResizer" in desktop
    assert "Exec=/opt/pycresizer/PycResizer" in desktop
    assert "Icon=pycresizer" in desktop
    assert "Terminal=false" in desktop


def test_windows_msi_definition_packages_pyinstaller_binary():
    wxs_path = ROOT / "packaging" / "windows" / "PycResizer.wxs"
    wxs = wxs_path.read_text(encoding="utf-8")

    assert "<Package" in wxs
    assert "Name=\"PycResizer\"" in wxs
    assert "Manufacturer=\"PycResizer\"" in wxs
    assert "<MajorUpgrade" in wxs
    assert "<MediaTemplate" in wxs
    assert "ProgramFiles64Folder" in wxs
    assert "Source=\"$(var.SourceDir)\\PycResizer.exe\"" in wxs
    assert "<Shortcut" in wxs
    assert "ApplicationProgramsFolder" in wxs
