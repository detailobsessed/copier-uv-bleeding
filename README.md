<p align="center">
  <img src="docs/assets/bleeding-edge-header.svg" alt="copier-uv-bleeding" width="800">
</p>

<p align="center">
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/actions?query=workflow%3Aci"><img src="https://github.com/detailobsessed/copier-uv-bleeding/workflows/ci/badge.svg" alt="CI"></a>
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/actions?query=workflow%3Arelease"><img src="https://github.com/detailobsessed/copier-uv-bleeding/workflows/release/badge.svg" alt="Release"></a>
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/releases"><img src="https://img.shields.io/github/v/release/detailobsessed/copier-uv-bleeding" alt="GitHub Release"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.15+-blue.svg" alt="Python 3.15+"></a>
</p>

This project strives to be the absolute best general-purpose [uv](https://github.com/astral-sh/uv) Python template in the universe. One `copier copy` gives you a fully configured, production-ready project with the latest and greatest Python tooling — no boilerplate, no compromises.

It is designed to be used as a starting point for new Python projects, providing all the essential tooling and configuration out of the box so you don't have to fuck around with project setup but can immediately start coding. Seriously.

> **🔥 BLEEDING EDGE** — This template intentionally targets the very latest stable release of Python and every tool in its stack. It strives to follow best practices for everything but completely disregards backwards compatibility. If you want safe and conservative, look elsewhere. If you want *modern and uncompromising*, you're in the right place.

> **⚡ Zero Configuration** — Once you run `copier copy`, everything is ready to go. No need to configure linters, formatters, or test runners. They're all set up with sensible defaults that follow modern Python best practices and are optimized for productivity, safety and maximum code quality.

> **🔄 Regular Updates** — This template is actively maintained and updated--a lot. Prepare to create a snippet for `copier update --trust` 😃.

> **🤝 Contributions Welcome** — This project is open to contributions! See the [Contributing Guide](CONTRIBUTING.md) for how to get started. Anybody want to take a stab at a better header image?

> **🙏 Acknowledgments** — This project originated as a fork of [pawamoy/copier-uv](https://github.com/pawamoy/copier-uv) by [Timothée Mazzucotelli](https://github.com/pawamoy), whose excellent work provided the foundation. It has since diverged significantly in scope and philosophy. Much of the modern tooling advice incorporated here is inspired by the [Python Developer Tooling Handbook](https://pydevtools.com/handbook/) — an outstanding resource for anyone serious about Python development.

## What You Get

- **[uv](https://github.com/astral-sh/uv)** — the fastest Python package manager, used for everything (deps, venvs, builds, lockfiles)
- **[ruff](https://github.com/astral-sh/ruff)** — 25+ rule categories for linting, formatting, security scanning, and dead code detection
- **[ty](https://github.com/astral-sh/ty)** — next-gen type checker from Astral (fast, modern, replaces mypy)
- **[complexipy](https://github.com/rohaquinlop/complexipy)** — cognitive complexity check per function, on every commit and in `poe check`
- **[prek](https://github.com/j178/prek)** — Rust-powered pre-commit hook runner (replaces pre-commit)
- **[poethepoet](https://github.com/nat-n/poethepoet)** — task runner with pre-configured tasks for every workflow
- **[pytest](https://github.com/pytest-dev/pytest)** — testing with coverage and randomization
- **[semantic-release](https://github.com/python-semantic-release/python-semantic-release)** — automated versioning and changelogs from conventional commits
- **[betterleaks](https://github.com/betterleaks/betterleaks)** — secret scanning on every commit (detects API keys, tokens, and credentials in staged changes)
- **[lychee](https://github.com/lycheeverse/lychee)** — fast link checking in CI
- **[sync-with-uv](https://github.com/tsvikas/sync-with-uv)** — auto-sync pre-commit hook versions from `uv.lock`
- **GitHub Actions / GitLab CI** — fully configured CI with Dependabot, Codecov, and optional Blacksmith runners
- **40+ open source licenses** from [choosealicense.com](https://choosealicense.com/appendix/)
- **uv build backend** — native build system, no setuptools

## Scaffold Prompts

When you run `copier copy`, you'll be asked:

| Prompt | Key | Description |
| ------ | --- | ----------- |
| **Project name** | `project_name` | Name of your project |
| **Project description** | `project_description` | One-line description |
| **Project type** | `project_type` | `app` (CLI entry point, like `uv init --app`) or `lib` (importable package, like `uv init --lib`) |
| **Author info** | `author_fullname`, `author_email`, `author_username` | Name, email, username (set defaults once per machine, see below) |
| **Repository provider** | `repository_provider` | `github.com` or `gitlab.com` |
| **Repository host** | `repository_host` | Hostname — override for self-hosted GitLab (e.g. `gitlab.company.com`) |
| **Repository namespace** | `repository_namespace` | GitHub/GitLab username or organization |
| **Open-source this project?** | `open_source` | Adds a LICENSE plus `CODE_OF_CONDUCT`, `CONTRIBUTING`, `SECURITY`, issue/PR templates and `FUNDING`. Off = internal/private, none of those. Defaults on for GitHub |
| **License** | `copyright_license` | Choose from 40+ open source licenses (asked only when open-sourcing) |
| **Enable semantic-release?** | `use_semantic_release` | Automated versioning and changelog |
| **Publish to PyPI?** | `publish_to_pypi` | Include PyPI publishing in release workflow (asked only with semantic-release) |
| **Publish to MCP Registry?** | `publish_to_mcp_registry` | Include the MCP Registry publish workflow (asked only when publishing to PyPI) |
| **Package index URL** | `custom_pypi_index_url` | Artifactory, Nexus, etc. Blank = PyPI |
| **Use Blacksmith runners?** | `use_blacksmith_runners` | 2x faster, 75% cheaper CI runners (GitHub only) |

The **Key** column names each answer in `.copier-answers.yml`, and is what `-d key=value` and the `defaults:` in copier's settings file take.

Every project gets CI (GitHub Actions or GitLab CI) and no test hooks on push. CI runs the whole test suite with coverage (`poe test-cov`): GitHub uploads it to Codecov, GitLab shows the total on merge requests. On GitHub, copy and update also run `gh repo edit` to enable delete-branch-on-merge and auto-merge, once the project has its own git repository and `gh` can reach it.

## Quick Start

### Install copier (one-time)

```bash
uv tool install copier
```

The template needs no Jinja extensions, so a stock copier is enough.

### Answer defaults per machine (optional)

Copier reads defaults for any template's questions from its user settings file: `~/Library/Application Support/copier/settings.yml` on macOS, `~/.config/copier/settings.yml` on Linux, or the path in `COPIER_SETTINGS_PATH`. Set your author details once and every prompt defaults to them:

```yaml
defaults:
  author_fullname: Jane Doe
  author_email: jane@example.com
  author_username: janedoe
```

A work machine can default `repository_host`, `repository_namespace` or `open_source: false` the same way, without the template knowing any internal hostname.

### Create a new project

```bash
copier copy --trust "gh:detailobsessed/copier-uv-bleeding" /path/to/your/new/project
```

### Or use uvx for zero-install one-shot runs

```bash
uvx copier copy --trust https://github.com/detailobsessed/copier-uv-bleeding.git my-project
```

The template automatically runs `uv sync --upgrade` and `prek install` after scaffolding.
Create your source files in `src/<package_name>/` and tests in `tests/`.

> **⚠️ Workflow permissions:** If semantic-release fails with 401 Unauthorized, your org or repo likely defaults `GITHUB_TOKEN` to read-only. See [Workflow Permissions](https://github.com/detailobsessed/ci-components#workflow-permissions) in ci-components for the fix.

## Adopting in an Existing Project

Already have a Python project and want to retrofit this template onto it? Copier supports adoption today, though it's not yet a first-class workflow — see the open feature request [`copier-org/copier#2486`](https://github.com/copier-org/copier/issues/2486).

From inside your existing project:

```bash
copier copy --trust "gh:detailobsessed/copier-uv-bleeding" .
```

Copier prompts on every file conflict. The template's `_skip_if_exists` list auto-preserves the files you actually own: `README.md`, `CHANGELOG.md`, your `src/` package, and your existing tests. For shared config like `pyproject.toml` and `prek.toml`, accept the template version and merge your project-specific bits (dependencies, custom hooks, ruff overrides) back in afterwards via `git diff`.

That first run writes `.copier-answers.yml`. From then on, `poe update-template` performs a proper 3-way merge that preserves your customizations.

> **Tip:** Run inside a clean working tree so `git diff` is your single source of truth for what changed. Pass `-f` to skip all prompts and overwrite everything not in `_skip_if_exists` — fastest path, but you'll be reconciling more by hand.

## Automatic Template Update Checking

Generated projects include a **post-checkout git hook** that automatically checks for template updates. When a newer version is available, you'll see a notification after `git checkout` / `git pull` / `git rebase`.

- **Manual check:** `poe check-template`
- **Apply updates:** `poe update-template` (runs `copier update` with smart 3-way merge), then `poe upgrade`

## Available Tasks

All projects come with pre-configured [poethepoet](https://github.com/nat-n/poethepoet) tasks:

| Task | Description |
| ---- | ----------- |
| `poe setup` | Install dependencies with uv |
| `poe lint` | Check code with ruff |
| `poe format` | Format code with ruff |
| `poe typecheck` | Type check with ty |
| `poe complexity` | Check cognitive complexity with complexipy |
| `poe check` | Run lint + typecheck + complexity (parallel) |
| `poe fix` | Auto-fix lint issues and format |
| `poe test` | Run fast tests (skip slow) |
| `poe test-affected` | Run only tests affected by changes ([testmon](https://github.com/tarpas/pytest-testmon)) |
| `poe test-all` | Run all tests |
| `poe test-cov` | Run tests with coverage report |
| `poe prek` | Run all pre-commit hooks |
| `poe check-template` | Check for template updates (manual) |
| `poe update-template` | Apply template updates via copier |
| `poe upgrade` | Upgrade dependencies and hook versions |
