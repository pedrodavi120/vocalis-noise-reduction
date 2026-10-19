#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.0.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

DIST_DIR="$ROOT_DIR/dist"
BIN_SRC="$DIST_DIR/vocalis"

if [ ! -f "$BIN_SRC" ]; then
    echo "Error: $BIN_SRC not found. Please build with PyInstaller first." >&2
    exit 1
fi

APP_DIR="$(mktemp -d -t vocalis-appdir-XXXXXX)"
trap 'rm -rf "$APP_DIR"' EXIT

echo "==> Preparing AppDir in $APP_DIR..."
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/lib"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy binary
install -m 755 "$BIN_SRC" "$APP_DIR/usr/bin/vocalis"

# Copy desktop and icon
install -m 644 "$SCRIPT_DIR/vocalis.desktop" "$APP_DIR/vocalis.desktop"
if [ -f "$ROOT_DIR/logo.png" ]; then
    install -m 644 "$ROOT_DIR/logo.png" "$APP_DIR/vocalis.png"
    install -m 644 "$ROOT_DIR/logo.png" "$APP_DIR/.DirIcon"
    install -m 644 "$ROOT_DIR/logo.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/vocalis.png"
fi

# Create AppRun
cat <<'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/vocalis" "$@"
EOF
chmod 755 "$APP_DIR/AppRun"

# Check or download appimagetool
APPIMAGETOOL="${APPIMAGETOOL:-}"
if [ -z "$APPIMAGETOOL" ] && command -v appimagetool >/dev/null 2>&1; then
    APPIMAGETOOL="appimagetool"
fi

if [ -z "$APPIMAGETOOL" ]; then
    echo "==> Downloading appimagetool..."
    TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    curl -sL "$TOOL_URL" -o /tmp/appimagetool
    chmod +x /tmp/appimagetool
    # In container or CI, extract appimagetool if FUSE is unavailable
    if ! /tmp/appimagetool --version >/dev/null 2>&1; then
        echo "==> Extracting appimagetool (no FUSE environment)..."
        (cd /tmp && ./appimagetool --appimage-extract >/dev/null)
        APPIMAGETOOL="/tmp/squashfs-root/AppRun"
    else
        APPIMAGETOOL="/tmp/appimagetool"
    fi
fi

mkdir -p "$DIST_DIR"
APPIMAGE_OUTPUT="$DIST_DIR/Vocalis-${VERSION}-x86_64.AppImage"

echo "==> Generating AppImage: $APPIMAGE_OUTPUT..."
ARCH=x86_64 "$APPIMAGETOOL" "$APP_DIR" "$APPIMAGE_OUTPUT"

echo "==> AppImage created successfully: $APPIMAGE_OUTPUT"
