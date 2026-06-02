# Code Review Guide

Targeted advice for reviewers of pull requests in this repository.

## What This Project Is

This is a **Copier template** that generates Python projects. Changes here don't run directly — they produce scaffolded projects via `copier copy`. Every change must be evaluated through that lens: *"will the generated output be correct for all combinations of user answers?"*

## Highest-Priority Review Areas

### 1. Jinja Template Rendering (`project/`)

Templates under `project/` are rendered with user-supplied strings. This is the most fragile surface area.

- **String escaping** — User inputs (project name, description, author name) are interpolated into TOML, YAML, Markdown, and Python files. Verify that quotes, backslashes, and special characters are properly escaped. See `pyproject.toml.jinja` lines using `replace('\\', '\\\\') | replace('\"', '\\\"')` for the pattern.
- **Conditional blocks** — `{% if %}` / `{% endif %}` guards control which sections appear based on boolean answers (`use_ci`, `use_semantic_release`, `publish_to_pypi`, `open_source`, etc.). Verify that every branch produces valid output and that no stray blank lines or missing newlines break structured formats.
- **TOML/YAML validity** — A misplaced Jinja block can produce syntactically invalid TOML or YAML. The test suite catches this, but eyeball the rendered output mentally for each conditional path.

### 2. Copier Configuration (`copier.yml`)

This file controls the entire scaffolding behavior.

- **Boolean cascading** — Questions like `use_semantic_release` depend on `use_ci` via `when` clauses. Changing defaults or conditions can silently break downstream answers. Trace the full dependency chain: `use_ci` -> `use_semantic_release` -> `publish_to_pypi` -> `use_blacksmith_runners`.
- **`_skip_if_exists` vs `_exclude`** — These have very different semantics. `_skip_if_exists` preserves user files during `copier update`. `_exclude` removes files entirely based on answers. Misplacing a file in the wrong list can overwrite user customizations or leave orphaned files.
- **`_tasks`** — Post-generation tasks run shell commands. Verify they are idempotent and safe for both `copy` and `update` operations (check `_copier_operation` guards).

### 3. Template Extensions (`extensions.py`)

Custom Jinja filters used during rendering.

- **`slugify`** — Used to derive package names, CLI names, and repository names from `project_name`. Changes here affect every generated file that uses these derived values.

### 4. CI Workflows (`.github/workflows/` and `project/.github/workflows/`)

Two distinct sets of workflows exist:

- **Template repo CI** (`.github/workflows/`) — Runs tests on this repository itself. Uses Blacksmith runners, path filtering, and pinned action SHAs.
- **Generated project CI** (`project/.github/workflows/*.jinja`) — Templates for the CI that generated projects will use. These are Jinja templates and must be reviewed with the same rigor as any other template file.

For both:

- **Pinned action SHAs** — All `uses:` references must pin to full commit SHAs, not tags. Verify the SHA matches the claimed version in the comment.
- **Blacksmith runner conditionals** — Generated workflows switch between `blacksmith-*` and `ubuntu-latest` runners based on `use_blacksmith_runners`. Verify both paths.
- **`setup-uv` has `github-token`** — Every `setup-uv` step needs `github-token: ${{ secrets.GITHUB_TOKEN }}` to avoid rate limiting.

### 5. Pre-commit Configuration (`prek.toml` and `project/prek.toml.jinja`)

- **Hook version pinning** — Versions are synced from `uv.lock` via `sync-with-uv`. When updating hook versions, verify they match the lockfile.
- **`default_install_hook_types`** — Controls which git hooks are installed. Adding or removing hook types affects the developer experience.
- **Stage assignments** — Some hooks run at `commit-msg`, others at `pre-push`. Verify hooks are assigned to appropriate stages.

### 6. Test Suite (`tests/`)

- **`test_template.py`** — Generates actual projects via `copier copy -r HEAD` and asserts on the output. Tests are module-scoped and cached — they must be **read-only** (no modifying generated project directories).
- **`test_template_lint.py`** — Renders every Jinja template against multiple context variants and validates TOML/YAML/Markdown/Python syntax. Also includes hypothesis-based string fuzzing. If you add a new boolean question or context variant, add a corresponding entry to `CONTEXT_VARIANTS`.
- **`conftest.py`** — The `project_factory` fixture caches generations by answer key. Changes to default answers affect all tests using `copier_defaults`.

## Common Pitfalls

- **Adding a new copier question** without updating `CONTEXT_VARIANTS` in `test_template_lint.py` and `copier_defaults` in `conftest.py`
- **Changing `_skip_if_exists`** without considering the impact on existing users running `copier update`
- **Template whitespace** — Jinja's whitespace control (`{%-`, `-%}`) matters in TOML and YAML. A missing hyphen can introduce blank lines that break parsing.
- **Forgetting to update both** `prek.toml` (template repo) **and** `project/prek.toml.jinja` (generated projects) when changing hook configuration
- **Semantic release config** exists in both `pyproject.toml` (template repo) and `project/pyproject.toml.jinja` (generated projects) — keep them consistent where appropriate

## Commit Messages

This project enforces [conventional commits](https://www.conventionalcommits.org/) via a pre-commit hook. Allowed types: `feat`, `fix`, `perf`, `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `test`. Semantic-release uses these to determine version bumps.

## Quick Checklist

- [ ] Templates render valid output for all boolean combinations
- [ ] String interpolation handles quotes, backslashes, and Unicode
- [ ] `copier.yml` question dependencies are consistent
- [ ] CI action SHAs are pinned and match claimed versions
- [ ] Both template-repo and generated-project configs are updated
- [ ] Tests cover new questions/variants
- [ ] No user-owned files are accidentally overwritten on `copier update`
