"""Post-update task: regenerate pyproject.toml/prek.toml from the template on
every `copier update`, while preserving explicitly marked user-owned regions
verbatim (DOT-599).

Both files mix template-owned config (most of the file) with sections users
grow over time (dependencies, [project.scripts], [dependency-groups],
[[tool.uv.index]], custom hooks) in one file, by design — the user of this
template prefers one file over splitting config out.

Copier's default `copier update` is NOT a true 3-way merge — it replays the
diff between the old and new template renders as a patch, using fuzzy
context matching. On a release that heavily restructures a file, that patch
can find *some* plausible anchor nearby and silently overwrite a hand-edited
section, WITHOUT producing a `.rej` file. That's what DOT-599 is named
after.

This borrows an idea from a small third-party tool, Templator
(github.com/dariusgm/templator, MIT, its "preserve_sections" feature)
rather than depending on it: wrap user-owned regions in
`# template-preserve:<name>:start` / `# template-preserve:<name>:end`
comments directly in the .jinja source. On every `copier update`, this
script snapshots those named regions from the CURRENT file, renders a fresh
copy of the whole file from the template, and splices the snapshotted
content back into the matching named regions of the fresh render.

Two deliberate deviations from Templator's own implementation (read from a
local clone, not assumed):
  1. Templator matches marked regions *positionally* (Nth occurrence to Nth
     occurrence). A release that reorders or inserts a marked region can
     silently splice content into the wrong slot. This script matches
     **by name** instead — immune to reordering/insertion.
  2. Templator empties any marked region with no snapshot, even on first
     generation (confirmed in its own test suite) — a footgun for a
     template that seeds real default content inside a marked region (e.g.
     this template's CLI entry point in [project.scripts]). This script
     never runs on first generation at all (`_tasks` gates it to
     update/recopy — see copier.yml), and even so, leaves a region's fresh
     default content untouched whenever there's no snapshot for that name,
     rather than blanking it.

Runs via `uv run --with copier --with copier-template-extensions` (see
copier.yml) rather than bare python3, unlike migrations/0.41.0_open_source.py:
this script needs copier's own renderer (which in turn needs
copier-template-extensions to load this template's `_jinja_extensions`) to
get an authoritative "what should this file look like now" answer — not
guaranteed importable in the destination project's own environment. PyYAML
is available transitively through copier. No TOML library needed at all —
this works on any text format that supports `#`-style comments.
"""

from __future__ import annotations

import errno
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import copier
import yaml

ANSWERS_FILE = Path(".copier-answers.yml")

# Files this script keeps in sync. Each is in `_skip_if_exists` in copier.yml,
# so Copier's default engine never touches them after first generation — this
# script is the only thing that updates them after that.
MANAGED_FILES: tuple[str, ...] = ("pyproject.toml", "prek.toml")

_MARKER_RE = re.compile(
    r"# template-preserve:(?P<name>[\w-]+):start\n(?P<body>.*?)# template-preserve:(?P=name):end\n",
    re.DOTALL,
)


def _load_answers() -> dict[str, Any]:
    if not ANSWERS_FILE.is_file():
        return {}
    raw = yaml.safe_load(ANSWERS_FILE.read_text(encoding="utf-8")) or {}
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def extract_named_sections(text: str) -> dict[str, str]:
    """Snapshot the content of every marked region in `text`, keyed by name."""
    return {m.group("name"): m.group("body") for m in _MARKER_RE.finditer(text)}


def splice_named_sections(new_text: str, preserved: dict[str, str]) -> str:
    """Replace each marked region in `new_text` with its preserved content,
    for every name that was actually snapshotted. Regions with no snapshot
    (new to this release, or the file was never customized) keep the fresh
    render's own default content untouched."""

    def _replace(match: re.Match[str]) -> str:
        name = match.group("name")
        if name not in preserved:
            return match.group(0)
        return f"# template-preserve:{name}:start\n{preserved[name]}# template-preserve:{name}:end\n"

    return _MARKER_RE.sub(_replace, new_text)


# --- Legacy bootstrap ---------------------------------------------------
#
# A project generated *before* this marker mechanism existed has none of the
# `# template-preserve:*` comments at all. Without this section, that
# project's first update to a marker-aware template version would silently
# replace every now-marked region with the fresh render's bare default —
# including real user data like hand-added dependencies. Caught in review
# on the PR that introduced markers, before it ever shipped (DOT-599).
#
# For the four structural, single-location regions, a regex anchored on the
# TOML syntax the template itself renders is enough to relocate the
# equivalent pre-marker content. `extra-poe-tasks`/`extra-local-hooks` have
# no single anchor — a hand-added task/hook sits mixed in among the
# template's own — so those two use an allowlist of the template's own
# known names to identify what's an addition, and physically move it (not
# copy: leaving it in both places would be a duplicate TOML key).
#
# Self-terminating: once a file has real markers, `missing` below is empty
# and this whole section is a no-op on every subsequent sync.

_LEGACY_LOCATORS: dict[str, re.Pattern[str]] = {
    "dependencies": re.compile(r"dependencies = \[.*?\]\n", re.DOTALL),
    "project-scripts": re.compile(r"\[project\.scripts\]\n.*?\n\n", re.DOTALL),
    "dependency-groups": re.compile(r"\[dependency-groups\]\n.*?\n\n", re.DOTALL),
    "tool-uv-index": re.compile(r"\[\[tool\.uv\.index\]\]\n.*?\n", re.DOTALL),
}

# Task/hook names the template itself defines, as of this release. Consulted
# ONLY during legacy bootstrap, to tell a hand-added task/hook apart from a
# template one in a file that predates the extra-poe-tasks/extra-local-hooks
# markers — never during normal (already-marked) syncing.
_KNOWN_POE_TASK_KEYS = {
    "setup",
    "lint",
    "format",
    "typecheck",
    "test",
    "test-affected",
    "test-all",
    "test-cov",
    "check",
    "fix",
    "prek",
    "check-template",
    "update-template",
    "tags",
    "actionsup",
    "releases",
    "runs",
    "checks",
    "watch",
}
_KNOWN_LOCAL_HOOK_IDS = {"no-copier-rej-files", "ty", "pytest-testmon", "pytest-cov", "check-template-update"}

_POE_TABLE_RE = re.compile(r"\[tool\.poe\.tasks\]\n(?P<body>.*?)(?=\n\[|\Z)", re.DOTALL)
_TASK_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)(?:\.[A-Za-z0-9_-]+)?\s*=")
_LOCAL_REPO_RE = re.compile(r'repo = "local"\n(?P<body>.*?)(?=\n\[\[repos\]\]|\Z)', re.DOTALL)
_HOOK_BLOCK_RE = re.compile(r"\[\[repos\.hooks\]\]\n.*?(?=\n\[\[repos\.hooks\]\]|\Z)", re.DOTALL)
_HOOK_ID_RE = re.compile(r'^id = "([^"]+)"', re.MULTILINE)


def _bootstrap_structural_markers(existing_text: str, missing: set[str]) -> str:
    for name in missing:
        locator = _LEGACY_LOCATORS.get(name)
        if locator is None:
            continue
        match = locator.search(existing_text)
        if match is None:
            continue  # genuinely nothing there (e.g. no custom PyPI index) — correct as-is
        wrapped = f"# template-preserve:{name}:start\n{match.group(0)}# template-preserve:{name}:end\n"
        existing_text = existing_text[: match.start()] + wrapped + existing_text[match.end() :]
    return existing_text


def _bootstrap_extra_poe_tasks(existing_text: str) -> str:
    match = _POE_TABLE_RE.search(existing_text)
    if match is None:
        return existing_text
    lines = match.group("body").splitlines(keepends=True)
    extra_lines = [ln for ln in lines if (m := _TASK_KEY_RE.match(ln)) and m.group(1) not in _KNOWN_POE_TASK_KEYS]
    if not extra_lines:
        return existing_text
    kept_lines = [ln for ln in lines if ln not in extra_lines]
    block = "# template-preserve:extra-poe-tasks:start\n" + "".join(extra_lines) + "# template-preserve:extra-poe-tasks:end\n"
    replacement = f"[tool.poe.tasks]\n{''.join(kept_lines)}{block}"
    return existing_text[: match.start()] + replacement + existing_text[match.end() :]


def _bootstrap_extra_local_hooks(existing_text: str) -> str:
    match = _LOCAL_REPO_RE.search(existing_text)
    if match is None:
        return existing_text
    body = match.group("body")
    extra_blocks = [
        b.group(0)
        for b in _HOOK_BLOCK_RE.finditer(body)
        if (id_match := _HOOK_ID_RE.search(b.group(0))) and id_match.group(1) not in _KNOWN_LOCAL_HOOK_IDS
    ]
    if not extra_blocks:
        return existing_text
    kept_body = body
    for block in extra_blocks:
        kept_body = kept_body.replace(block, "", 1)
    kept_body = re.sub(r"\n{3,}", "\n\n", kept_body).strip("\n")
    extras = "\n".join(b if b.endswith("\n") else f"{b}\n" for b in extra_blocks)
    block = f"# template-preserve:extra-local-hooks:start\n{extras}# template-preserve:extra-local-hooks:end\n"
    replacement = f'repo = "local"\n{kept_body}\n\n{block}'
    return existing_text[: match.start()] + replacement + existing_text[match.end() :]


def _bootstrap_legacy_markers(existing_text: str, fresh_text: str) -> str:
    """See module comment above. Returns `existing_text` with markers added
    around any pre-marker content for names that `fresh_text` expects but
    `existing_text` doesn't have yet."""
    missing = set(extract_named_sections(fresh_text)) - set(extract_named_sections(existing_text))
    if not missing:
        return existing_text
    existing_text = _bootstrap_structural_markers(existing_text, missing)
    if "extra-poe-tasks" in missing:
        existing_text = _bootstrap_extra_poe_tasks(existing_text)
    if "extra-local-hooks" in missing:
        existing_text = _bootstrap_extra_local_hooks(existing_text)
    return existing_text


def sync_text(existing_text: str, new_text: str) -> str:
    """Pure merge: `new_text` (a fresh template render) with every marked
    region in `existing_text` preserved verbatim. Everything outside marked
    regions always reflects `new_text` — that's the whole point."""
    existing_text = _bootstrap_legacy_markers(existing_text, new_text)
    preserved = extract_named_sections(existing_text)
    return splice_named_sections(new_text, preserved)


def _render_fresh(src_path: str, answers: dict[str, Any], dst: Path) -> None:
    # vcs_ref="HEAD" matters: left as the default (None), copier.run_copy
    # resolves to the *latest git tag* of src_path, not its checked-out
    # working tree. At real update time src_path is `_copier_conf.src_path`
    # — Copier's own local clone already checked out at the exact version
    # this update resolved to — so HEAD of *that* clone is the correct,
    # already-resolved version, not "whatever the latest tag happens to be."
    try:
        copier.run_copy(
            src_path=src_path,
            dst_path=dst,
            data=answers,
            vcs_ref="HEAD",
            defaults=True,
            overwrite=True,
            quiet=True,
            unsafe=True,
            skip_tasks=True,
        )
    except OSError as exc:
        # Copier clones src_path into its own temp directory and rmtree's it
        # once rendering is done; on macOS that rmtree can lose a race
        # against Spotlight indexing the freshly-created .git directory,
        # raising `OSError: [Errno 66] Directory not empty` (ENOTEMPTY). That
        # happens in Worker.__exit__, strictly *after* rendering into `dst`
        # already completed — confirmed by inspection: `dst` is fully
        # populated every time this specific exception has been observed.
        # Narrowly scoped on purpose (per review): only swallow that exact
        # errno, and only when every file we actually came here for is
        # present — anything else (a real rendering failure that happens to
        # leave some partial output) still raises instead of silently
        # leaving managed files stale.
        if exc.errno != errno.ENOTEMPTY or not all((dst / name).is_file() for name in MANAGED_FILES):
            raise


def main() -> None:
    existing_files = [f for f in MANAGED_FILES if Path(f).is_file()]
    if not existing_files:
        return  # fresh copy — Copier's normal engine already wrote these correctly

    src_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent)
    answers = _load_answers()

    with tempfile.TemporaryDirectory() as tmp:
        render_dir = Path(tmp) / "render"
        _render_fresh(src_path, answers, render_dir)

        for name in existing_files:
            fresh = render_dir / name
            if not fresh.is_file():
                continue
            existing_text = Path(name).read_text(encoding="utf-8")
            merged = sync_text(existing_text, fresh.read_text(encoding="utf-8"))
            if merged != existing_text:
                Path(name).write_text(merged, encoding="utf-8")


if __name__ == "__main__":
    main()
