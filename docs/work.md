# Working on a project

The generated project has this structure:

```
📁 your_project ------------------- # your freshly created project!
├── 📄 .pre-commit-config.yaml ---- # pre-commit hooks configuration
├── 📄 CHANGELOG.md --------------- #
├── 📄 CODE_OF_CONDUCT.md --------- #
├── 📄 CONTRIBUTING.md ------------ #
├── 📁 docs ----------------------- # documentation pages
│   ├── 📄 changelog.md ----------- #
│   ├── 📄 code_of_conduct.md ----- #
│   ├── 📄 contributing.md -------- #
│   ├── 📁 css -------------------- # extra CSS files
│   │   ├── 📄 material.css ------- #
│   │   └── 📄 mkdocstrings.css --- #
│   ├── 📄 index.md --------------- #
│   └── 📄 license.md ------------- #
├── 📄 LICENSE -------------------- #
├── 📄 mkdocs.yml ----------------- # docs configuration
├── 📄 pyproject.toml ------------- # project metadata, dependencies, tools config, and tasks
├── 📄 README.md ------------------ #
├── 📁 src ------------------------ # the source code directory
│   └── � your_package ----------- # your package
│       ├── � _internal ---------- # internal implementation
│       │   ├── � cli.py --------- # CLI implementation (typer or argparse)
│       │   └── 📄 debug.py ------- # debug utilities
│       ├── 📄 __init__.py -------- # re-exports main and app/get_parser
│       ├── 📄 __main__.py -------- # python -m entry point
│       └── 📄 py.typed ----------- # PEP 561 marker
└── 📁 tests ---------------------- # the tests directory
    ├── 📄 conftest.py ------------ # pytest fixtures
    ├── 📄 __init__.py ------------ #
    ├── 📄 test_api.py ------------ # API tests
    └── 📄 test_cli.py ------------ # CLI tests
```

## Environment

The project is configured to use [direnv](https://direnv.net/).
If direnv is loaded in your shell, allow it in the project with
`direnv allow`. The .envrc file doesn't add anything to PATH anymore
since we use poe for all tasks.

In the rest of the documentation, we will use `poe` commands.

See [Tasks](#tasks) to learn more.

## Python versions

This template requires **Python 3.14+** (bleeding edge).
The generated project will use Python 3.14 as the minimum version.

## Initialize Git Repository

This project uses dynamic versioning based on Git tags. Initialize your project as a Git repository:

```
git init .
```

## Dependencies and virtual environments

Dependencies are managed by [uv](https://github.com/astral-sh/uv).

Use `poe setup` or `uv sync` to install the dependencies.

Dependencies are written in `pyproject.toml`.
Runtime dependencies are listed under the `[project]` and `[project.optional-dependencies]` sections,
and development dependencies are listed under the `[dependency-groups]` section.

Example:

```toml title="pyproject.toml"
[project]
dependencies = [
  "fastapi>=1.0",
  "importlib-metadata>=2.0",
]

[project.optional-dependencies]
test = [
  "pytest",
]

[dependency-groups]
ci = [
  "ruff",
]
```

## Tasks

The project uses [poe the poet](https://github.com/nat-n/poethepoet) as a task runner.
Tasks are defined in `pyproject.toml` under the `[tool.poe.tasks]` section.

Example:

```toml title="pyproject.toml"
[tool.poe.tasks]
check_docs = "mkdocs build -s"
```

To run a task, use `poe TASK [ARGS...]`.
You can run multiple tasks at once: `poe TASK1 TASK2`.
You can list the available tasks with `poe --help`.

Available tasks:

- `setup`: Install project dependencies.
- `lint`: Check the code quality with ruff.
- `format`: Run ruff formatter on the code.
- `typecheck`: Check that the code is correctly typed with ty.
- `check`: Run all quality checks (lint + typecheck).
- `fix`: Auto-fix lint issues and format code.
- `test`: Run the test suite.
- `test-cov`: Run the test suite with coverage.
- `docs`: Serve the documentation (localhost:8000).
- `docs-build`: Build the documentation.
- `docs-deploy`: Deploy the documentation to GitHub Pages.
- `prek`: Run all pre-commit hooks.

## Additional Commands

You can run arbitrary commands with uv:

- `uv run command --args`: Run commands in the virtual environment.
  Example: `uv run python` to start Python without activating the venv.

### VSCode setup

If you work in VSCode, we provide a `poe vscode` task
that configures settings and tasks. **It will overwrite the following existing
files, so make sure to back them up:**

- `.vscode/launch.json`
- `.vscode/settings.json`
- `.vscode/tasks.json`

## Workflow

The first thing you should run when entering your repository is:

```bash
poe setup
```

If you don't have the `make` command,
you can use `poe setup` directly,
or even just `uv venv; uv pip install`
if you don't plan on using multiple Python versions.

This will install the project's dependencies in virtual environments:
one venv per chosen Python version in `.venvs/$python_version`,
and one default venv in `.venv/`.

The chosen Python versions are defined in the `PYTHON_VERSIONS` environment variable.

Now you can start writing and editing code in `src/your_package`.

- You can auto-format the code with `poe format`.
- You can run a quality analysis with `poe check`.
- Once you wrote tests for your new code,
  you can run the test suite with `poe test`.
- Once you are ready to publish a new release,
  run `poe changelog`, then `poe release version=x.y.z`,
  where `x.y.z` is the version added to the changelog.

To summarize, the typical workflow is:

```bash
poe setup  # only once

<write code>
poe format  # to auto-format the code

<write tests>
poe test  # to run the test suite

poe check  # to check if everything is OK

<commit your changes>

poe changelog  # to update the changelog
<edit changelog if needed>

poe release version=x.y.z
```

## Quality analysis

The quality checks are started with:

```
poe check
```

This action is actually a composition of several checks:

- `lint`: Check the code quality with ruff.
- `typecheck`: Check if the code is correctly typed with ty.

For example, if you are only interested in checking types,
run `poe typecheck`.

### lint

The code quality analysis is done
with [Ruff](https://github.com/astral-sh/ruff).
The analysis is configured in `pyproject.toml` under `[tool.ruff]`.
You can deactivate rules or activate others to customize your analysis.
Rules identifiers always start with one or more capital letters,
like `D`, `S` or `BLK`, then followed by a number.

You can ignore a rule on a specific code line by appending
a `noqa` comment ("no quality analysis/assurance"):

```python title="src/your_package/module.py"
print("a code line that triggers a Ruff warning")  # noqa: ID
```

...where ID is the identifier of the rule you want to ignore for this line.

Example:

```python title="src/your_package/module.py"
import subprocess
```

```console
$ poe lint
src/your_package/module.py:2:1: S404 Consider possible security implications associated with subprocess module.
```

Now add a comment to ignore this warning.

```python title="src/your_package/module.py"
import subprocess  # noqa: S404
```

```console
$ poe lint
✓ Checking code quality
```

You can disable multiple different warnings on a single line
by separating them with commas:

```python title="src/your_package/module.py"
markdown_docstring = """
    Look at this docstring:

    ```python
    \"\"\"
    print("code block")
    \"\"\"
    ```
"""  # noqa: D300,D301
```

You can disable a warning globally by adding its ID
to the ignore list in `pyproject.toml`.

You can also disable warnings per file, like so:

```toml title="pyproject.toml"
[tool.ruff.lint.per-file-ignores]
"src/your_package/your_module.py" = [
    "T201",  # Print statement
]
```

### check-docs

This action builds the documentation with strict behavior:
any warning will be considered an error and the command will fail.

The warnings/errors can be about incorrect docstring format,
or invalid cross-references.

See the [Documentation section](#documentation) for more information.

### typecheck

This action runs [`ty`](https://github.com/astral-sh/ty) on the source code
to find potential typing errors. ty is a fast type checker from Astral (the makers of ruff and uv).

## Tests

Run the test suite with:

```
poe test
```

Behind the scenes, it uses [`pytest`](https://docs.pytest.org/en/stable/)
and plugins to collect and run the tests, and output a report.

Code source coverage is computed thanks to
[coveragepy](https://coverage.readthedocs.io/en/coverage-5.1/).

Sometimes you don't want to run the whole test suite,
but rather one particular test, or group of tests.
Pytest provides a `-k` option to allow filtering the tests:

```
uv run pytest -k training
uv run pytest -k "app and route2"
```

## Continuous Integration

The quality checks and tests are executed in parallel
in a [GitHub Workflow](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions).
The CI is configured in `.github/workflows/ci.yml`.

## Changelog

Changelogs are absolutely useful when your software
is updated regularly, to inform your users about the new features
that were added or the bugs that were fixed.

But writing a changelog manually is a cumbersome process.

This is why we offer, with this template,
a way to automatically update the changelog.
There is one requirement though for it to work:
you must use the
[Angular commit message convention](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).

For a quick reference:

```
<type>[(scope)]: Subject

[Body]
```

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes which are not features nor bug fixes.
- `style`: A change in code style/format.
- `tests`: About tests.

The two most important are `feat` and `fix` types.
For other types of commits, you can do as you like.

Subject (and body) must be valid Markdown.
If you write a body, please add issues references at the end:

```
Body.

References: #10, #11.
Fixes #15.
```

Examples:

```
feat: Add training route
```

```
fix: Stop deleting user data
```

Following that convention will allow to generate
new entries in the changelog while following the rules
of [semantic versioning](https://semver.org/).

Once you are ready to publish a new release of your package,
run the following command:

```
poe changelog
```

This will update the changelog in-place, using the latest,
unpublished-yet commits.

If this group of commits contains only bug fixes (`fix:`)
and/or commits that are not interesting for users (`chore:`, `style:`, etc.),
the changelog will gain a new **patch** entry.
It means that the new suggested version will be a patch bump
of the previous one: `0.1.1` becomes `0.1.2`.

If this group of commits contains at least one feature (`feat:`),
the changelog will gain a new **minor** entry.
It means that the new suggested version will be a minor bump
of the previous one: `0.1.1` becomes `0.2.0`.

If there is, in this group, a commit whose body contains
something like `Breaking change`,
the changelog will gain a new **major** entry,
unless the version is still an "alpha" version
(starting with 0), in which case it gains a **minor** entry.
It means that the new suggested version will be a major bump
of the previous one: `1.2.1` becomes `2.0.0`,
but `0.2.1` is only bumped up to `0.3.0`.
Moving from "alpha" status to "beta" or "stable" status
is a choice left to the developers,
when they consider the package is ready for it.

## Releases

This template uses [python-semantic-release](https://python-semantic-release.readthedocs.io/)
for automated versioning and releases. When you push to main with conventional commits,
the GitHub Actions workflow will:

1. Analyze commits to determine version bump (patch/minor/major)
2. Update the version in `pyproject.toml`
3. Generate/update `CHANGELOG.md`
4. Create a git tag
5. Build and publish to PyPI (if configured)
6. Create a GitHub release

## Documentation

The documentation is built with [Mkdocs](https://www.mkdocs.org/),
the [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/) theme,
and the [mkdocstrings](https://mkdocstrings.github.io/) plugin.

### Writing

The pages are written in Markdown, and thanks to `mkdocstrings`,
even your Python docstrings can be written in Markdown.
`mkdocstrings` particularly supports the
[Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
for docstrings.

The documentation configuration is written into `mkdocs.yml`,
at the root of the project. The Markdown pages are written
in the `docs/` directory. You can use any level of nesting you want.
The left-sidebar navigation is configured through the `nav` key
in `mkdocs.yml`.

For example, with these docs structure:

```
📁 docs
├── 📄 changelog.md
├── 📄 index.md
└── 📁 reference
    ├── 📄 cli.md
    └── 📄 logic.md
```

...you can have these navigation items in `mkdocs.yml`:

```yaml title="mkdocs.yml"
nav:
- Overview: index.md
- Code Reference:
  - cli.py: reference/cli.md
  - logic.py: reference/logic.md
- Changelog: changelog.md
```

Note that we matched the sections in the navigation with the folder tree,
but that is not mandatory.

`mkdocstrings` allows you to inject documentation of Python objects
in Markdown pages with the following syntax:

```md
::: path.to.object
    OPTIONS
```

...where `OPTIONS` is a YAML block containing configuration options
for both the selection of Python objects and their rendering.

You can document an entire module or even package with a single instruction:

```md
::: your_package
```

...but it's usually better to have each module injected in a separate page.

The generated projects will by default render only the top-level module in the API reference page.
The template expects that all the API be exposed at the top-level. If you expose public submodules,
add a new page for each one of these submodules.

For more information about `mkdocstrings`,
check [its documentation](https://mkdocstrings.github.io).

### Serving

MkDocs provides a development server with files watching and live-reload.
Run `poe docs` to serve your documentation on `localhost:8000`.

### Deploying

MkDocs has a `gh-deploy` command that will deploy
your documentation on GitHub pages:

```bash
poe docs-deploy
```
