<p align="center">
  <img src="docs/assets/bleeding-edge-header.svg" alt="copier-uv-bleeding" width="800">
</p>

<p align="center">
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/actions?query=workflow%3Aci"><img src="https://github.com/detailobsessed/copier-uv-bleeding/workflows/ci/badge.svg" alt="CI"></a>
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/actions?query=workflow%3Arelease"><img src="https://github.com/detailobsessed/copier-uv-bleeding/workflows/release/badge.svg" alt="Release"></a>
  <a href="https://github.com/detailobsessed/copier-uv-bleeding/releases"><img src="https://img.shields.io/github/v/release/detailobsessed/copier-uv-bleeding" alt="GitHub Release"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.14+-blue.svg" alt="Python 3.14+"></a>
</p>

> **⚠️ Requires Python 3.14+** — This template targets the latest stable Python release only.
>
> **This is a fork of [pawamoy/copier-uv](https://github.com/pawamoy/copier-uv).**
> Huge thanks to [Timothée Mazzucotelli](https://github.com/pawamoy) for the excellent original template!

[Copier](https://github.com/copier-org/copier) template
for Python projects managed by [uv](https://github.com/astral-sh/uv).

## What's Different in This Fork

- **[ty](https://github.com/astral-sh/ty)** instead of mypy for type checking (fast, modern, from Astral)
- **[prek](https://github.com/prek-org/prek)** instead of pre-commit (faster, written in Rust)
- **[poethepoet](https://github.com/nat-n/poethepoet)** task runner with pre-configured tasks
- **Comprehensive ruff rules** - 18 rule categories including security (S), unused args (ARG), and more
- **No standalone bandit/vulture** - ruff handles security scanning and dead code detection
- **No version pins** - get the latest versions at scaffold time
- **[uv build backend](https://docs.astral.sh/uv/concepts/build-backend/)** - native uv build system

## Scaffold Prompts

When you run `copier copy`, you'll be asked:

| Prompt | Description |
| ------ | ----------- |
| **Project name** | Name of your project |
| **Project description** | One-line description |
| **Project type** | `app` (script), `lib` (library), or `package` (CLI tool) |
| **Author info** | Name, email, username (auto-detected from git) |
| **Repository provider** | `github.com` or `gitlab.com` |
| **Repository namespace** | GitHub/GitLab username or organization |
| **License** | Choose from 40+ open source licenses |
| **Enable CI?** | GitHub Actions or GitLab CI for testing, linting, type checking |
| **Enable semantic-release?** | Automated versioning and changelog (requires CI) |
| **Publish to PyPI?** | Include PyPI publishing in release workflow |
| **Use Blacksmith runners?** | 2x faster, 75% cheaper CI runners |
| **Enable Polar.sh?** | Sponsorship integration |
| **Existing project?** | Skip generating scaffolding files (CLI, tests) for existing codebases |

### Recommended Reading

- [Sync with uv: Eliminate pre-commit version drift](https://pydevtools.com/blog/sync-with-uv-eliminate-pre-commit-version-drift/)

## Features

- [uv](https://github.com/astral-sh/uv) setup, with pre-defined `pyproject.toml`
- Pre-configured tools for code formatting, quality analysis and testing:
  [ruff](https://github.com/astral-sh/ruff) (linting, formatting, security, dead code),
  [ty](https://github.com/astral-sh/ty) (type checking),
  [pytest](https://github.com/pytest-dev/pytest) (testing)
- Tests run with [pytest](https://github.com/pytest-dev/pytest) and plugins, with [coverage](https://github.com/nedbat/coveragepy) support
- Documentation built with [MkDocs](https://github.com/mkdocs/mkdocs)
  ([Material theme](https://github.com/squidfunk/mkdocs-material)
  and "autodoc" [mkdocstrings plugin](https://github.com/mkdocstrings/mkdocstrings))
- Modern Python tooling with [uv](https://github.com/astral-sh/uv), [ruff](https://github.com/astral-sh/ruff), and [poethepoet](https://github.com/nat-n/poethepoet)
- Support for GitHub Actions and GitLab CI with Dependabot
- Auto-generated `CHANGELOG.md` from Git (conventional) commits
- All licenses from [choosealicense.com](https://choosealicense.com/appendix/)

## Quick Start

### Install copier (one-time)

```bash
# Install copier with required Jinja extensions
uv tool install copier --with copier-templates-extensions
```

### Create a new project

```bash
copier copy --trust "gh:detailobsessed/copier-uv-bleeding" /path/to/your/new/project
```

### Or use uvx for zero-install one-shot runs

```bash
uvx --with copier-templates-extensions \
  copier copy --trust https://github.com/detailobsessed/copier-uv-bleeding.git my-project
```

### Adopt into an existing project

> **Note:** The `adopt` command is available via [my fork](https://github.com/detailobsessed/copier/tree/feat/adopt-command) while the [upstream PR](https://github.com/copier-org/copier/pull/2487) ([issue](https://github.com/copier-org/copier/issues/2486)) is in review.

```bash
# Install the fork with adopt support
uv tool install copier \
  --from "git+https://github.com/detailobsessed/copier.git@feat/adopt-command" \
  --with copier-templates-extensions

# Adopt the template in your existing project
copier adopt --trust --conflict inline https://github.com/detailobsessed/copier-uv-bleeding.git .
```

To update the fork later, re-run the install command with `--force`.

The template automatically runs `uv sync` and `prek install` after scaffolding.

## Available Tasks

All projects come with pre-configured [poethepoet](https://github.com/nat-n/poethepoet) tasks:

| Task | Description |
| ---- | ----------- |
| `poe setup` | Install dependencies with uv |
| `poe lint` | Check code with ruff |
| `poe format` | Format code with ruff |
| `poe typecheck` | Type check with ty |
| `poe check` | Run lint + typecheck |
| `poe fix` | Auto-fix lint issues and format |
| `poe test` | Run fast tests (skip slow) |
| `poe test-all` | Run all tests |
| `poe test-cov` | Run tests with coverage |
| `poe docs` | Serve docs locally |
| `poe prek` | Run all pre-commit hooks |
| `poe reset-and-adopt` | Reset and re-adopt template (preserves answers) |
| `poe runs` | List recent CI runs |
| `poe watch` | Watch current CI run |
