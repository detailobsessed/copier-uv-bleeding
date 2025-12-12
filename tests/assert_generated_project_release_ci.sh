#!/usr/bin/env bash
set -eu

fail() {
    echo "FAIL: $1" >&2
    exit 1
}

[ -f pyproject.toml ] || fail "pyproject.toml not found"
[ -f .github/workflows/ci.yml ] || fail ".github/workflows/ci.yml not found"
[ -f .github/workflows/release.yml ] || fail ".github/workflows/release.yml not found"

grep -q "^\[build-system\]" pyproject.toml || fail "pyproject.toml missing [build-system]"

grep -q "uses: astral-sh/setup-uv@v7" .github/workflows/ci.yml || fail "ci.yml missing setup-uv@v7"

grep -q "uv run semantic-release version" .github/workflows/release.yml || fail "release.yml missing uv-run semantic-release"

grep -q "Check if release artifacts exist" .github/workflows/release.yml || fail "release.yml missing dist/* gating step"

grep -q "uv publish" .github/workflows/release.yml || fail "release.yml missing uv publish"

echo "OK: generated CI/release assertions passed"
