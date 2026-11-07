// Command SubMeson is the Bambleweeny 57 emulator proxy: it executes the ROM path
// it is handed as a child process and exits with that process's status.
package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"strings"
)

// version is the build version, replaced at build time with
// -ldflags "-X main.version=<tag>". "dev" marks a build from source.
var version = "dev"

const usageText = `SubMeson — Bambleweeny 57 emulator proxy

Usage:
  SubMeson [flags] <path-to-rom>

Flags:
  -v, --version   print the version and exit
  -h, --help      print this help and exit

SubMeson executes the ROM path it is handed and exits with that process's status.
It has no ROM registry and no extension filter — the frontend owns the
ROM-to-emulator mapping.
`

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

// run keeps the process exit in one place so the command can be exercised
// without spawning a binary.
func run(args []string, stdout, stderr io.Writer) int {
	var rom string
	endOfFlags := false
	for _, arg := range args {
		if !endOfFlags {
			switch arg {
			case "-v", "--version":
				fmt.Fprintf(stdout, "SubMeson %s\n", version)
				return 0
			case "-h", "--help":
				fmt.Fprint(stdout, usageText)
				return 0
			case "--":
				endOfFlags = true
				continue
			}
			if strings.HasPrefix(arg, "-") {
				fmt.Fprintf(stderr, "SubMeson: unknown flag %q\n\n", arg)
				fmt.Fprint(stderr, usageText)
				return 2
			}
		}
		if rom != "" {
			fmt.Fprintf(stderr, "SubMeson: unexpected argument %q\n\n", arg)
			fmt.Fprint(stderr, usageText)
			return 2
		}
		rom = arg
	}
	if rom == "" {
		fmt.Fprint(stderr, "SubMeson: no ROM given\n\n")
		fmt.Fprint(stderr, usageText)
		return 2
	}
	return launch(rom, stdout, stderr)
}

// launch routes .app bundles through open, because exec cannot run a bundle directory.
// open -W bounds one app and forwards its exit status; plain open returns immediately.
func launch(rom string, stdout, stderr io.Writer) int {
	cmd := exec.Command(rom)
	if info, err := os.Stat(rom); err == nil && info.IsDir() && strings.HasSuffix(rom, ".app") {
		cmd = exec.Command("open", "-W", rom)
	}
	cmd.Stdin = os.Stdin
	cmd.Stdout = stdout
	cmd.Stderr = stderr

	err := cmd.Run()
	if err == nil {
		return 0
	}
	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		return exitErr.ExitCode()
	}
	fmt.Fprintf(stderr, "SubMeson: %v\n", err)
	return 1
}
