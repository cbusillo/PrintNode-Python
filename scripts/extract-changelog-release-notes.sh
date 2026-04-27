#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: scripts/extract-changelog-release-notes.sh --version VERSION --output FILE

Extracts the matching CHANGELOG.md section for a GitHub Release body.
USAGE
}

version=""
output=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      version="${2:-}"
      shift 2
      ;;
    --output)
      output="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$version" || -z "$output" ]]; then
  usage
  exit 2
fi

version="${version#v}"

awk -v version="$version" '
  /^## / {
    if (in_section) {
      exit
    }
    heading = $0
    if (heading ~ "^## " version "( - |$)") {
      in_section = 1
      print heading
      next
    }
  }
  in_section { print }
' CHANGELOG.md > "$output"

if [[ ! -s "$output" ]]; then
  {
    echo "## $version"
    echo ""
    echo "See CHANGELOG.md for release details."
  } > "$output"
fi

cat >> "$output" <<'NOTES'

## Package

This is a community-maintained PrintNode API client published as `printnode_community`.
NOTES
