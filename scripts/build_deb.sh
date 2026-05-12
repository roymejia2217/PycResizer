#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
APP_NAME="${APP_NAME:-PycResizer}"
PACKAGE_NAME="${PACKAGE_NAME:-pycresizer}"
PACKAGE_SUMMARY="${PACKAGE_SUMMARY:-Batch image resizer}"
PACKAGE_DESCRIPTION="${PACKAGE_DESCRIPTION:-Desktop batch image processor built with Python, Tkinter, ttkbootstrap, and Pillow.}"
MAINTAINER="${MAINTAINER:-PycResizer Maintainers <maintainers@example.invalid>}"
PACKAGE_DEPENDS="${PACKAGE_DEPENDS:-libc6}"
INSTALL_ROOT="${INSTALL_ROOT:-/opt/pycresizer}"
BINARY_PATH="${BINARY_PATH:-${PROJECT_ROOT}/dist/${APP_NAME}}"
DESKTOP_FILE="${DESKTOP_FILE:-${PROJECT_ROOT}/packaging/linux/pycresizer.desktop}"
ICON_FILE="${ICON_FILE:-${PROJECT_ROOT}/docs/logo.png}"
LICENSE_FILE="${LICENSE_FILE:-${PROJECT_ROOT}/LICENSE}"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/dist/packages}"
BUILD_ROOT="${BUILD_ROOT:-${PROJECT_ROOT}/build/deb}"

if [[ -n "${PACKAGE_VERSION:-}" ]]; then
  VERSION="${PACKAGE_VERSION}"
elif [[ -n "${GITHUB_REF_NAME:-}" ]]; then
  VERSION="${GITHUB_REF_NAME#v}"
else
  VERSION="$(git -C "${PROJECT_ROOT}" describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || true)"
  VERSION="${VERSION:-0.0.0}"
fi

if [[ -n "${PACKAGE_ARCHITECTURE:-}" ]]; then
  ARCHITECTURE="${PACKAGE_ARCHITECTURE}"
else
  ARCHITECTURE="$(dpkg --print-architecture)"
fi

PACKAGE_ROOT="${BUILD_ROOT}/${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}"
PACKAGE_FILE="${OUTPUT_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"

require_file() {
  local path="$1"
  local label="$2"
  if [[ ! -f "${path}" ]]; then
    echo "Required ${label} is missing: ${path}" >&2
    exit 1
  fi
}

require_command() {
  local name="$1"
  if ! command -v "${name}" >/dev/null 2>&1; then
    echo "Required command is missing: ${name}" >&2
    exit 1
  fi
}

require_command dpkg-deb
require_file "${BINARY_PATH}" "application binary"
require_file "${DESKTOP_FILE}" "desktop entry"
require_file "${ICON_FILE}" "application icon"
require_file "${LICENSE_FILE}" "license file"

rm -rf "${PACKAGE_ROOT}"
mkdir -p \
  "${PACKAGE_ROOT}/DEBIAN" \
  "${PACKAGE_ROOT}${INSTALL_ROOT}" \
  "${PACKAGE_ROOT}/usr/share/applications" \
  "${PACKAGE_ROOT}/usr/share/icons/hicolor/256x256/apps" \
  "${PACKAGE_ROOT}/usr/share/doc/${PACKAGE_NAME}" \
  "${OUTPUT_DIR}"

install -m 0755 "${BINARY_PATH}" "${PACKAGE_ROOT}${INSTALL_ROOT}/${APP_NAME}"
install -m 0644 "${DESKTOP_FILE}" "${PACKAGE_ROOT}/usr/share/applications/${PACKAGE_NAME}.desktop"
install -m 0644 "${ICON_FILE}" "${PACKAGE_ROOT}/usr/share/icons/hicolor/256x256/apps/${PACKAGE_NAME}.png"
install -m 0644 "${LICENSE_FILE}" "${PACKAGE_ROOT}/usr/share/doc/${PACKAGE_NAME}/copyright"

cat > "${PACKAGE_ROOT}/DEBIAN/control" <<CONTROL
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCHITECTURE}
Maintainer: ${MAINTAINER}
Depends: ${PACKAGE_DEPENDS}
Description: ${PACKAGE_SUMMARY}
 ${PACKAGE_DESCRIPTION}
CONTROL

chmod 0755 "${PACKAGE_ROOT}/DEBIAN"
chmod 0644 "${PACKAGE_ROOT}/DEBIAN/control"

dpkg-deb --root-owner-group --build "${PACKAGE_ROOT}" "${PACKAGE_FILE}"
dpkg-deb --info "${PACKAGE_FILE}"
dpkg-deb --contents "${PACKAGE_FILE}"

echo "Debian package created: ${PACKAGE_FILE}"
