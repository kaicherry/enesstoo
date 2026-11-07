# SubMeson — Bambleweeny 57 emulator proxy

A passthrough launcher, not an emulator with a ROM registry.

`SubMeson` executes the path it is handed and forwards the exit status verbatim. No ROM registry, no name lookup, no extension filter, no rewrite. The frontend owns ROM-to-emulator mapping.

- Repo dir: `EnessToo`
- Go module: `github.com/kaicherry/enesstoo`
- Go: 1.22
- Third-party dependencies: none
- Product file: `cmd/SubMeson/main.go` (formerly `bm42`)

## Usage

```sh
SubMeson [flags] <path-to-rom>
```

Flags:

- `-v`, `--version` — print `SubMeson <version>` (`dev` by default; override with `-ldflags "-X main.version=<tag>"`)
- `-h`, `--help` — print usage
- `--` — end flags

Bundle paths (`.app` directories) launch via `open -W`, because `exec` cannot run a bundle directory. The path is not rewritten.

For frontends: launch the binary (e.g. `dist/SubMeson.app/Contents/MacOS/SubMeson`) for exact exit forwarding. `open -W SubMeson.app --args <path>` waits for GUI apps but cannot reliably capture instant-exit CLI children.

Exit codes:

- Child status forwarded verbatim
- No ROM, second positional, or unknown dash-flag: `2`
- Unexecutable path: `1`
- `-v` / `-h`: `0`

## Build

From source, always run these at the module root:

```sh
go build ./...
go vet ./...
```

Never run bare `go build` / `go vet` at the module root — there are no Go files there.

Plain build:

```sh
go build -o SubMeson ./cmd/SubMeson
```

## Distributions

Binaries are gitignored (`/SubMeson`, `/dist/`, `*.syso`, `localTmp/`, `.DS_Store`). Obtain binaries from a GitHub release or build from source.

### macOS

```sh
./scripts/build-darwin-app.sh
```

Builds:

- `dist/SubMeson.app`
- `dist/SubMeson.dmg`

Unsigned test bundle; runs as-is.

Packaging:

- `packaging/darwin/Info.plist` — `CFBundleIdentifier com.rnsksoftronics.SubMeson`, `CFBundleExecutable SubMeson`, `APPL`, short version `1.0`, `LSMinimumSystemVersion 12.0`, `arm64`, category utilities, `NSHighResolutionCapable`
- `packaging/darwin/appicon.png` (512×512) → `Contents/Resources/AppIcon.icns` via `sips` / `iconutil`
- `Contents/PkgInfo` is `APPL????`

Sign / notarize / staple commands use Developer ID Application: Ronin no Sakura Kai Softronics (`MPUGVKL8KJ`) and `xcrun notarytool` / `stapler`. An `impressium` hook may wrap them; exact commands are in the script header.

### Windows

```sh
./scripts/build-windows-exe.sh
```

Builds:

- `dist/SubMeson.exe` — PE32+ console x86-64, `GOOS=windows GOARCH=amd64`

Packaging:

- `packaging/windows/appicon.ico` (256×256 PNG-in-ICO) embedded via `github.com/akavel/rsrc` temp `.syso` (cleaned on exit)

Unsigned test build.

## Frontend contract

See `docs/specs/submeson-frontend-contract.md` for the full frontend contract: emulator identity, no required extensions, launch syntax.

## Layout

- `cmd/SubMeson/main.go` — only product file
- `packaging/darwin/Info.plist`, `packaging/darwin/appicon.png` — macOS bundle
- `packaging/windows/appicon.ico` — Windows icon
- `scripts/build-darwin-app.sh`, `scripts/build-windows-exe.sh` — distribution builds
- `docs/specs/submeson-frontend-contract.md` — frontend contract
- `docs/STATE.md`, `docs/donot.md` — project state and do-not list
- `go.mod` — module definition
