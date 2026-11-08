# SubMeson — Bambleweeny 57 emulator proxy

A passthrough launcher, not an emulator, created as a simple "proxy console" from "front end" emulator launchers.
The "use case" is a simple one: many games from older systems are being made into 'recomps' - ports from game systems,
to "standalone native apps/programs".

The *problem* is that front ends associate "roms" with "consoles/systems" - something 'recomps' do not inherently "have".

Instead, `SubMeson` is registered as the "emulator" for a "console" (say, an N64 or PSX) and ".exe/.app" (or eny extension you choose)
is registered as the "rom extension"...allowing your 'recomps" to appear as roms for the system they originally ran on. Like any other
"rom" when selected via the frontend/launcher, the frontend calls/runs SubMeson, supplied the path to the recomp, and runs it, no need
for "wrapper scripts" or "config files"...it just works like any other (actual) emulator would.

`SubMeson` executes a path it is handed and forwards the exit status verbatim. 
No ROM registry, no name lookup, no extension filter, no rewrite. Your frontend owns ROM-to-emulator mapping.

## Usage

```sh
SubMeson [flags] <path-to-rom>
```

Flags:

- `-v`, `--version` — print `SubMeson <version>` (`dev` by default; override with `-ldflags "-X main.version=<tag>"`)
- `-h`, `--help` — print usage
- `--` — end flags

On macs undle paths (`.app` directories) launch via plain `open` (no `-W`), because `exec` cannot run a bundle directory. The path is not rewritten. Plain `open` returns immediately, so `SubMeson` exits when `open` does, not when the app quits.

For frontends: launch the binary (e.g. `dist/SubMeson.app/Contents/MacOS/SubMeson`) for exact exit forwarding of plain binaries.

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

## Layout

- `cmd/SubMeson/main.go` — only product file
- `packaging/darwin/Info.plist`, `packaging/darwin/appicon.png` — macOS bundle
- `packaging/windows/appicon.ico` — Windows icon
- `scripts/build-darwin-app.sh`, `scripts/build-windows-exe.sh` — distribution builds
- `docs/specs/submeson-frontend-contract.md` — frontend contract
- `docs/STATE.md`, `docs/donot.md` — project state and do-not list
- `go.mod` — module definition
