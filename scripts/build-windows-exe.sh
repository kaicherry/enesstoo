#!/usr/bin/env bash
# Build the SubMeson Windows exe with appicon.ico embedded (unsigned test build).
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${VERSION:-dev}"
DIST="dist"
EXE="$DIST/SubMeson.exe"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"; rm -f cmd/SubMeson/rsrc_windows_amd64.syso' EXIT

mkdir -p "$DIST"
GOBIN="$TMP/bin" go install github.com/akavel/rsrc@latest
(cd cmd/SubMeson && "$TMP/bin/rsrc" -arch amd64 -ico ../../packaging/windows/appicon.ico)
GOOS=windows GOARCH=amd64 go build -trimpath -ldflags "-X main.version=${VERSION}" -o "$EXE" ./cmd/SubMeson

echo "Built $EXE"
