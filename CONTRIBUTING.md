# Contributing

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Environment setup

You need three tools: [uv](https://github.com/astral-sh/uv),
[Copier](https://github.com/copier-org/copier), and [prek](https://github.com/j178/prek).

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install copier with its required Jinja extensions
#    copier must be on PATH — the test suite calls it as a subprocess
uv tool install copier --with copier-templates-extensions

# 3. Install prek (git hook runner)
curl -LsSf https://github.com/j178/prek/releases/latest/download/prek-installer.sh | sh
```

Then clone the repository, install Python dependencies, and set up git hooks:

```bash
git clone https://github.com/detailobsessed/copier-uv-bleeding
cd copier-uv-bleeding
poe setup       # installs Python dependencies (uv sync)
prek install    # installs git hooks
```

## Running tests

```bash
poe test
```

The test suite generates real projects via `copier copy`, so `copier` must be installed
and on PATH (see step 2 above). Tests that call `uv sync` on generated projects also
require `uv` on PATH.

## Serving docs

```bash
poe docs
```
