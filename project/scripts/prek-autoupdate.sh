#!/usr/bin/env bash
# Wraps `uv run prek autoupdate` with a workaround for lychee marking `nightly` as
# their GitHub "Latest" release (DOT-492). The second pass with --cooldown-days 7
# reverts lychee's `rev` from `nightly` back to the most recent versioned tag.
# Remove once lychee stops marking nightly as Latest (DOT-504).
set -eu
uv run prek autoupdate "$@"
uv run prek autoupdate --repo https://github.com/lycheeverse/lychee --cooldown-days 7 "$@"
