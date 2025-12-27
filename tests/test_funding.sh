#!/usr/bin/env bash
set -eu

# Test FUNDING.yml generation with and without polar

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

fail() {
    echo "FAIL: $1" >&2
    exit 1
}

test_without_polar() {
    local test_dir="/tmp/funding-test-no-polar-$$"
    trap "rm -rf ${test_dir}" RETURN

    echo ">>> Testing FUNDING.yml without polar (use_polar=false)"
    copier copy -f --trust -r HEAD "${REPO_ROOT}" "${test_dir}" \
        -d project_name="Test No Polar" \
        -d project_description="Testing" \
        -d author_username="testuser" \
        -d use_polar=false \
        >/dev/null 2>&1

    local funding_file="${test_dir}/.github/FUNDING.yml"
    [ -f "${funding_file}" ] || fail "FUNDING.yml not found"

    grep -q "^github: testuser$" "${funding_file}" || fail "FUNDING.yml missing github sponsor"
    if grep -q "^polar:" "${funding_file}"; then
        fail "FUNDING.yml should NOT contain polar when use_polar=false"
    fi

    echo "OK: FUNDING.yml correct without polar"
}

test_with_polar() {
    local test_dir="/tmp/funding-test-with-polar-$$"
    trap "rm -rf ${test_dir}" RETURN

    echo ">>> Testing FUNDING.yml with polar (use_polar=true)"
    copier copy -f --trust -r HEAD "${REPO_ROOT}" "${test_dir}" \
        -d project_name="Test With Polar" \
        -d project_description="Testing" \
        -d author_username="testuser" \
        -d use_polar=true \
        >/dev/null 2>&1

    local funding_file="${test_dir}/.github/FUNDING.yml"
    [ -f "${funding_file}" ] || fail "FUNDING.yml not found"

    grep -q "^github: testuser$" "${funding_file}" || fail "FUNDING.yml missing github sponsor"
    grep -q "^polar: testuser$" "${funding_file}" || fail "FUNDING.yml missing polar when use_polar=true"

    echo "OK: FUNDING.yml correct with polar"
}

test_without_polar
test_with_polar

echo
echo "==========================================="
echo "      FUNDING.YML TESTS PASSED ✓"
echo "==========================================="
