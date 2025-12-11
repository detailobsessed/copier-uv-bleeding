# Copier UV (Bleeding Edge Fork)

> **This is a fork of [pawamoy/copier-uv](https://github.com/pawamoy/copier-uv).**
> Huge thanks to [Timothée Mazzucotelli](https://github.com/pawamoy) for the excellent original template!

[Copier](https://github.com/copier-org/copier) template
for Python projects managed by [uv](https://github.com/astral-sh/uv).

## What's Different in This Fork

- **[ty](https://github.com/astral-sh/ty)** instead of mypy for type checking (fast, modern, from Astral)
- **[prek](https://github.com/prek-org/prek)** instead of pre-commit (faster, written in Rust)
- **[poethepoet](https://github.com/nat-n/poethepoet)** task runner
- **[bandit](https://github.com/PyCQA/bandit)** for security scanning
- **[vulture](https://github.com/jendrikseipp/vulture)** for dead code detection
- **[pyupgrade](https://github.com/asottile/pyupgrade)** for syntax modernization
- **No version pins** - get the latest versions at scaffold time
- **Dependabot** configured for uv and GitHub Actions
- **[commitlint](https://commitlint.js.org/)** for commit message enforcement (Angular/Conventional format)
- **[python-semantic-release](https://python-semantic-release.readthedocs.io/)** for automated versioning and releases
- **[uv build backend](https://docs.astral.sh/uv/concepts/build-backend/)** - native uv build system
- **Optional PyPI publishing** - prompted during scaffold, commented out if not needed

### Recommended Reading

- [Sync with uv: Eliminate pre-commit version drift](https://pydevtools.com/blog/sync-with-uv-eliminate-pre-commit-version-drift/)

## Features

- [uv](https://github.com/astral-sh/uv) setup, with pre-defined `pyproject.toml`
- Pre-configured tools for code formatting, quality analysis and testing:
  [ruff](https://github.com/charliermarsh/ruff),
  [ty](https://github.com/astral-sh/ty),
  [bandit](https://github.com/PyCQA/bandit),
  [vulture](https://github.com/jendrikseipp/vulture)
- Tests run with [pytest](https://github.com/pytest-dev/pytest) and plugins, with [coverage](https://github.com/nedbat/coveragepy) support
- Documentation built with [MkDocs](https://github.com/mkdocs/mkdocs)
  ([Material theme](https://github.com/squidfunk/mkdocs-material)
  and "autodoc" [mkdocstrings plugin](https://github.com/mkdocstrings/mkdocstrings))
- Cross-platform tasks with [duty](https://github.com/pawamoy/duty) and [poethepoet](https://github.com/nat-n/poethepoet)
- Support for GitHub workflows with Dependabot
- Auto-generated `CHANGELOG.md` from Git (conventional) commits
- All licenses from [choosealicense.com](https://choosealicense.com/appendix/)

## Quick setup and usage

```bash
copier copy --trust "gh:ichoosetoaccept/copier-uv-bleeding" /path/to/your/new/project
```

The template automatically runs `prek autoupdate` and `uv sync` after scaffolding.
