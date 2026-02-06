#!/usr/bin/env bash
# Reset working tree to a clean state for re-applying a copier template.
# Preserves .copier-answers.yml so copier reuses previous answers.
# Usage: ./scripts/reset-and-adopt.sh [-y]
#   -y  Skip confirmation prompt

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

auto_yes=false
while getopts "y" opt; do
    case $opt in
        y) auto_yes=true ;;
        *) echo "Usage: $0 [-y]" && exit 1 ;;
    esac
done

echo "=== Uncommitted changes ==="
git status --short
echo ""
echo "=== Untracked files (will be removed) ==="
git clean -fdn -e .copier-answers.yml
echo ""

if [ "$auto_yes" = false ]; then
    read -rp "This will discard ALL changes and untracked files (except .copier-answers.yml). Are you sure? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "Discarding all changes..."
if [ -f .copier-answers.yml ]; then
    cp .copier-answers.yml .copier-answers.yml.backup
fi
git reset --hard HEAD
git clean -fd -e .copier-answers.yml.backup
if [ -f .copier-answers.yml.backup ]; then
    mv .copier-answers.yml.backup .copier-answers.yml
fi

echo ""
echo "✓ Working tree reset to HEAD."
echo ""
echo "Next steps — run one of:"
echo "  copier recopy --trust .                    # re-apply template (standard copier)"
echo "  copier update --trust .                    # update to latest template version"
echo "  copier adopt --trust --conflict inline .   # adopt template (requires copier fork)"
