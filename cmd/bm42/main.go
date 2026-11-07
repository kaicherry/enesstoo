// Command bm42 is the Bambleweeny-42 emulator proxy: it takes a ROM name and
// executes the mapped binary. This build is the skeleton only — version, help,
// and usage — and answers no ROM yet.
package main

import (
	"fmt"
	"io"
	"os"
	"strings"
)

// version is the build version, replaced at build time with
// -ldflags "-X main.version=<tag>". "dev" marks a build from source.
var version = "dev"

const usageText = `bm42 — Bambleweeny-42 emulator proxy

Usage:
  bm42 [flags]

Flags:
  -v, --version   print the version and exit
  -h, --help      print this help and exit

ROM lookup and execution are not part of this build; it answers the
version and help flags and prints usage for anything else.
`

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

// run keeps the process exit in one place so the command can be exercised
// without spawning a binary.
func run(args []string, stdout, stderr io.Writer) int {
	for _, arg := range args {
		switch arg {
		case "-v", "--version":
			fmt.Fprintf(stdout, "bm42 %s\n", version)
			return 0
		case "-h", "--help":
			fmt.Fprint(stdout, usageText)
			return 0
		}
		if strings.HasPrefix(arg, "-") {
			fmt.Fprintf(stderr, "bm42: unknown flag %q\n\n", arg)
			fmt.Fprint(stderr, usageText)
			return 2
		}
	}
	fmt.Fprint(stdout, usageText)
	return 0
}
