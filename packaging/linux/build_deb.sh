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

DEB_BUILD_DIR="$(mktemp -d -t vocalis-deb-XXXXXX)"
trap 'rm -rf "$DEB_BUILD_DIR"' EXIT

echo "==> Preparing Debian package tree in $DEB_BUILD_DIR..."

mkdir -p "$DEB_BUILD_DIR/DEBIAN"
mkdir -p "$DEB_BUILD_DIR/usr/bin"
mkdir -p "$DEB_BUILD_DIR/usr/share/applications"
mkdir -p "$DEB_BUILD_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_BUILD_DIR/usr/share/pixmaps"
mkdir -p "$DEB_BUILD_DIR/usr/share/metainfo"
mkdir -p "$DEB_BUILD_DIR/usr/share/doc/vocalis"

# 1. Install application binary
install -m 755 "$BIN_SRC" "$DEB_BUILD_DIR/usr/bin/vocalis"

# 2. Install desktop launcher
install -m 644 "$SCRIPT_DIR/vocalis.desktop" "$DEB_BUILD_DIR/usr/share/applications/vocalis.desktop"

# 3. Install AppStream metadata
if [ -f "$SCRIPT_DIR/vocalis.metainfo.xml" ]; then
    install -m 644 "$SCRIPT_DIR/vocalis.metainfo.xml" "$DEB_BUILD_DIR/usr/share/metainfo/br.com.voidstudio.vocalis.metainfo.xml"
fi

# 4. Install desktop icons
if [ -f "$ROOT_DIR/logo.png" ]; then
    install -m 644 "$ROOT_DIR/logo.png" "$DEB_BUILD_DIR/usr/share/icons/hicolor/256x256/apps/vocalis.png"
    install -m 644 "$ROOT_DIR/logo.png" "$DEB_BUILD_DIR/usr/share/pixmaps/vocalis.png"
fi

# 5. Install package documentation & copyright
if [ -f "$ROOT_DIR/LICENSE" ]; then
    install -m 644 "$ROOT_DIR/LICENSE" "$DEB_BUILD_DIR/usr/share/doc/vocalis/copyright"
fi
if [ -f "$ROOT_DIR/README.md" ]; then
    install -m 644 "$ROOT_DIR/README.md" "$DEB_BUILD_DIR/usr/share/doc/vocalis/README.md"
fi

# 6. Install maintenance scripts (postinst and postrm)
if [ -f "$SCRIPT_DIR/postinst" ]; then
    install -m 755 "$SCRIPT_DIR/postinst" "$DEB_BUILD_DIR/DEBIAN/postinst"
fi
if [ -f "$SCRIPT_DIR/postrm" ]; then
    install -m 755 "$SCRIPT_DIR/postrm" "$DEB_BUILD_DIR/DEBIAN/postrm"
fi

# 7. Calculate Installed-Size in KiB according to Debian Policy
INSTALLED_SIZE="$(du -sk "$DEB_BUILD_DIR/usr" | awk '{print $1}')"

# 8. Generate standard control file
cat <<EOF > "$DEB_BUILD_DIR/DEBIAN/control"
Package: vocalis
Version: $VERSION
Section: sound
Priority: optional
Architecture: amd64
Installed-Size: $INSTALLED_SIZE
Depends: libportaudio2, libjack-jackd2-0 | libjack0, libasound2
Maintainer: Void Studio <contato@voidstudio.com.br>
Homepage: https://www.voidstudio.com.br
Description: AI-Powered Noise Reduction Studio & Virtual Microphone
 Vocalis is a high-performance desktop studio for real-time background
 noise suppression, acoustic filtering, and clean virtual microphone streaming.
EOF

mkdir -p "$DIST_DIR"
DEB_OUTPUT="$DIST_DIR/vocalis_${VERSION}_amd64.deb"

echo "==> Building Debian package: $DEB_OUTPUT..."
dpkg-deb --build --root-owner-group "$DEB_BUILD_DIR" "$DEB_OUTPUT"

echo "==> Debian package generated successfully: $DEB_OUTPUT"
