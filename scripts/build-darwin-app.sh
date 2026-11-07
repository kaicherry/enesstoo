#!/usr/bin/env bash
# Build the SubMeson darwin app bundle and DMG (unsigned test bundle).
#
# Sign/notarize/staple with a Developer ID Application identity, e.g.:
#   codesign --deep --force --options runtime --sign "Developer ID Application: Ronin no Sakura Kai Softronics (MPUGVKL8KJ)" dist/SubMeson.app
#   xcrun notarytool submit dist/SubMeson.dmg --apple-id <id> --team-id MPUGVKL8KJ --password <app-specific-password> --wait
#   xcrun stapler staple dist/SubMeson.app dist/SubMeson.dmg
# An impressium hook may wrap those steps.
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${VERSION:-dev}"
DIST="dist"
APP="$DIST/SubMeson.app"
DMG="$DIST/SubMeson.dmg"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

go build -trimpath -ldflags "-X main.version=${VERSION}" -o "$TMP/SubMeson" ./cmd/SubMeson

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cp "$TMP/SubMeson" "$APP/Contents/MacOS/SubMeson"
cp packaging/darwin/Info.plist "$APP/Contents/Info.plist"
printf 'APPL????' > "$APP/Contents/PkgInfo"
chmod +x "$APP/Contents/MacOS/SubMeson"

mkdir -p "$TMP/AppIcon.iconset"
for s in 16 32 64 128 256 512; do
  sips -z "$s" "$s" packaging/darwin/appicon.png --out "$TMP/AppIcon.iconset/icon_${s}x${s}.png" >/dev/null
done
sips -z 1024 1024 packaging/darwin/appicon.png --out "$TMP/AppIcon.iconset/icon_512x512@2x.png" >/dev/null
cp "$TMP/AppIcon.iconset/icon_32x32.png" "$TMP/AppIcon.iconset/icon_16x16@2x.png"
cp "$TMP/AppIcon.iconset/icon_64x64.png" "$TMP/AppIcon.iconset/icon_32x32@2x.png"
cp "$TMP/AppIcon.iconset/icon_256x256.png" "$TMP/AppIcon.iconset/icon_128x128@2x.png"
cp "$TMP/AppIcon.iconset/icon_512x512.png" "$TMP/AppIcon.iconset/icon_256x256@2x.png"
iconutil -c icns "$TMP/AppIcon.iconset" -o "$TMP/AppIcon.icns"
mkdir -p "$APP/Contents/Resources"
cp "$TMP/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"

mkdir -p "$TMP/dmg"
cp -R "$APP" "$TMP/dmg/SubMeson.app"
ln -s /Applications "$TMP/dmg/Applications"
hdiutil create -volname SubMeson -srcfolder "$TMP/dmg" -ov -format UDZO "$DMG"

echo "Built $APP"
echo "Built $DMG"
