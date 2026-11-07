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

mkdir -p "$TMP/dmg"
cp -R "$APP" "$TMP/dmg/SubMeson.app"
ln -s /Applications "$TMP/dmg/Applications"
hdiutil create -volname SubMeson -srcfolder "$TMP/dmg" -ov -format UDZO "$DMG"

echo "Built $APP"
echo "Built $DMG"
