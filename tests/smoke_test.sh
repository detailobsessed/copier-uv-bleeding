#!/usr/bin/env bash
set -eu

# Smoke test for the copier template
# Generates a project, runs checks, and cleans up

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEST_DIR="${TEST_DIR:-/tmp/copier-uv-smoke-test-$$}"

cleanup() {
    echo ">>> Cleaning up ${TEST_DIR}"
    rm -rf "${TEST_DIR}"
}
trap cleanup EXIT

echo
echo "==========================================="
echo "       COPIER-UV TEMPLATE SMOKE TEST"
echo "==========================================="
echo

echo ">>> Generating project in ${TEST_DIR}"
copier copy -f --trust -r HEAD "${REPO_ROOT}" "${TEST_DIR}" \
    -d project_name="Smoke Test Project" \
    -d project_description="Testing the template" \
    -d author_fullname="Test Author" \
    -d author_username="testuser" \
    -d author_email="test@example.com" \
    -d publish_to_pypi=true

cd "${TEST_DIR}"

echo
echo ">>> Checking generated files exist"
test -f pyproject.toml || { echo "FAIL: pyproject.toml not found"; exit 1; }
test -f .pre-commit-config.yaml || { echo "FAIL: .pre-commit-config.yaml not found"; exit 1; }
test -d src || { echo "FAIL: src/ directory not found"; exit 1; }
test -d tests || { echo "FAIL: tests/ directory not found"; exit 1; }
echo "OK: Core files present"

echo
echo ">>> Checking generated CI/release configuration"
bash "${REPO_ROOT}/tests/assert_generated_project_release_ci.sh"

echo
echo ">>> Initializing git repo (required for some tools)"
git init .
git add -A
git commit -m "feat: Initial commit"

echo
echo ">>> Running uv sync"
uv sync

echo
echo ">>> Running quality checks"
uv run poe check

echo
echo ">>> Running tests"
uv run poe test

echo
echo "==========================================="
echo "         SMOKE TEST PASSED ✓"
echo "==========================================="
