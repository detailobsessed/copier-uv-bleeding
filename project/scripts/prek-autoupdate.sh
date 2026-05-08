#!/usr/bin/env bash
# Wraps `uv run prek autoupdate` with a workaround for lychee tagging `nightly`
# as their GitHub "Latest" release (lycheeverse/lychee#1601). The
# --repo-exclude-tag flag (prek 0.3.11+) keeps lychee on its real latest
# versioned tag instead of flipping to `nightly`. Remove the flag when upstream
# closes lycheeverse/lychee#1601 (DOT-504).
set -eu
uv run prek autoupdate --repo-exclude-tag https://github.com/lycheeverse/lychee=nightly "$@"
