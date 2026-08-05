# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A **Copier template** that generates production-ready Python 3.14+ projects. The `project/` directory contains Jinja templates rendered by `copier copy`. Changes here don't run directly -- they produce scaffolded projects, so every change must be valid across all combinations of user answers.

## Issue Tracking

Linear issues for this repo live in the **`copier-uv-bleeding` project** on the `Detail Obsessed` (DOT) team. When working in this repo, only report on issues in that Linear project -- the DOT team also holds unrelated work (a macOS app, career/website tasks) that is noise here. `list_issues` takes `project: "copier-uv-bleeding"`.

Linear only auto-closes on a bare `Closes DOT-NNN` line -- `Refs DOT-NNN` attaches the PR without closing. **When adding a commit to an already-open PR, re-check the PR body's `Closes`/`Refs` lines**: a fix appended to a stack after the body was written closes nothing (DOT-629 shipped in #345 and stayed in Backlog for exactly this reason).

## Commands

```bash
poe setup          # uv sync
poe test           # fast tests (skip slow markers)
poe test-all       # all tests including slow
poe test-cov       # tests with coverage (90% threshold)
poe check          # lint + typecheck in parallel
poe fix            # auto-fix lint issues and format
poe prek           # run all pre-commit hooks
poe docs           # serve docs locally

# Single test
pytest tests/test_template.py::TestProjectTypes::test_app_type_has_cli -v
```

## Architecture

- **`project/`** -- Template source. Files ending in `.jinja` are rendered by Copier with user answers. This is the main editing surface.
- **`copier.yml`** -- Controls all scaffolding: prompts, defaults, conditional excludes, post-generation tasks. Boolean questions cascade: `use_ci` -> `use_semantic_release` -> `publish_to_pypi` / `publish_to_mcp_registry` -> `use_blacksmith_runners`.
- **`extensions.py`** -- Custom Jinja filters (`slugify`, `git_user_name/email/username`, `current_year`).
- **`tests/`** -- Template validation suite:
  - `conftest.py` -- `copier_defaults` fixture and `project_factory` (module-scoped, caches generated projects by answer key). Tests must be **read-only** on generated projects.
  - `test_template.py` -- Integration tests: generates real projects via `copier copy -r HEAD --skip-tasks`, asserts on output.
  - `test_template_lint.py` -- Property-based: renders Jinja templates against `CONTEXT_VARIANTS` (all boolean combos), validates TOML/YAML/Python/Markdown syntax. Hypothesis fuzzes string inputs.
  - `test_licenses.py` -- License file integrity and SPDX compliance.

## Critical Patterns

**Tests use `-r HEAD`** to test the current commit, not the last tag. `copier.yml` is read from the VCS ref, so uncommitted config changes to `copier.yml` won't be picked up by tests until committed.

**String escaping in templates** -- User inputs interpolated into TOML must escape backslashes and quotes: `replace('\\', '\\\\') | replace('"', '\\"')`.

**Jinja whitespace control** -- `{%-` and `-%}` matter in TOML/YAML. Missing hyphens introduce blank lines that break parsing.

**Dual configs** -- `prek.toml` (this repo) and `project/prek.toml.jinja` (generated projects) must both be updated for hook changes. Same for `pyproject.toml` vs `project/pyproject.toml.jinja` for semantic-release config.

**Adding a new copier question** requires updating: `copier.yml`, `CONTEXT_VARIANTS` in `test_template_lint.py`, and `copier_defaults` in `conftest.py`.

**`_skip_if_exists` vs `_exclude`** -- `_skip_if_exists` preserves user files during `copier update`. `_exclude` removes files based on answers. Misplacing a file in the wrong list can overwrite user customizations.

## Tooling Notes

**prek** -- TOML config (`prek.toml`), not YAML. `priority` schedules hooks: ascending order, same value runs concurrently, omitted means sequential-by-order. Per prek's reference, two hooks in one group that mutate the same files have **undefined** results, and a group that modifies files fails as a whole with no attribution to the responsible hook -- so a new fixing hook needs a priority no other hook writing those same files uses. Group 0 is read-only checks; builtin mutators are 1-4; group 5 holds fixers with disjoint file types, with `ruff-format` at 6 after `ruff --fix`. `prek util list-builtins` is the authoritative builtin id list. `[priorities]` alias tables need prek 0.4.11+. `files` accepts glob patterns via `files = { glob = ["docs/**"] }`. Use `prek util identify <file>` to debug type filters. `PREK_QUIET=1` suppresses passing hooks.

**ty** -- Reads `requires-python` from `pyproject.toml` to determine stdlib availability. If set too low, it won't resolve newer stdlib modules. Must be `>=3.14` for this template.

**actionlint** -- Cannot validate permissions of cross-repo reusable workflows. If a reusable workflow requests `id-token: write` but the caller only grants `contents: write`, actionlint won't catch it -- GitHub rejects at parse time.

**uv trusted publishing** -- PyPI OIDC trusted publishing does NOT work from reusable GitHub Actions workflows. The `job_workflow_ref` claim points to the reusable workflow's repo, not the caller's. Always run `uv publish` in the calling workflow.

**copier `_skip_if_exists` vs `_exclude`** -- `_skip_if_exists` skips overwriting if the file exists but creates it if missing. `_exclude` permanently prevents generation -- once excluded, `copier update` can never bring it back. Only use `_exclude` for feature-gated files.

## Commit Convention

Conventional commits enforced by prek hook. Allowed types: `feat`, `fix`, `perf`, `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `test`. `feat` = minor bump, most others = patch bump (aggressive, so template users get improvements via `copier update`).
