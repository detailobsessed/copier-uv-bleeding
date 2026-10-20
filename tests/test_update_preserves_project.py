"""A real `copier update` must never undo what a downstream project changed.

Every customisation below was lost by an actual update of an actual project
(DOT-620 and its comments). Unit tests on `sync_marked_sections.sync_text`
covered one key at a time and passed while those updates went out, so this
test runs the user's flow end to end instead: generate at a released tag,
customise the way a project does, commit, `copier update` to HEAD with its
tasks, then check each customisation on its own so a failure names the loss.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The release the reporting project was on before its last destructive update.
BASELINE_TAG = "0.41.14"

# `copier_defaults` is function-scoped, so the module fixture below cannot use it.
# `use_heavy_hooks` puts the pytest-cov hook (and its `--cov-fail-under`) in prek.toml.
ANSWERS = {
    "project_name": "Test Project",
    "project_description": "A test project",
    "author_fullname": "Test Author",
    "author_email": "test@example.com",
    "author_username": "testuser",
    "repository_namespace": "testuser",
    "copyright_license": "MIT",
    "open_source": True,
    "use_ci": True,
    "use_semantic_release": True,
    "publish_to_pypi": False,
    "use_blacksmith_runners": False,
    "configure_repo_settings": False,
    "use_heavy_hooks": True,
    "project_type": "app",
}

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


@dataclass(frozen=True)
class Customisation:
    """One downstream change: text edits to apply, and what must hold after the update."""

    id: str
    file: str
    edits: tuple[tuple[str | None, str], ...]  # (anchor, replacement); a None anchor appends
    present: tuple[str, ...] = ()
    absent: tuple[str, ...] = ()


CUSTOMISATIONS = (
    # --- pyproject.toml ---------------------------------------------------
    Customisation(
        "released-version",
        "pyproject.toml",
        (('version = "0.0.0"', 'version = "0.18.0"'),),
        present=('version = "0.18.0"',),
    ),
    Customisation(
        "tag-format",
        "pyproject.toml",
        (('tag_format = "{version}"', 'tag_format = "v{version}"'),),
        present=('tag_format = "v{version}"',),
    ),
    Customisation(
        "dependencies",
        "pyproject.toml",
        (("dependencies = []", 'dependencies = ["httpx>=0.28"]'),),
        present=('dependencies = ["httpx>=0.28"]',),
    ),
    Customisation(
        "build-backend-window",
        "pyproject.toml",
        (('"uv_build>=0.12.1,<0.13"', '"uv_build>=0.13,<0.14"'),),
        present=('"uv_build>=0.13,<0.14"',),
    ),
    Customisation(
        "project-urls",
        "pyproject.toml",
        (
            (
                'Funding = "https://github.com/sponsors/testuser"',
                'Funding = "https://github.com/sponsors/testuser"\nDocumentation = "https://docs.example.com"',
            ),
        ),
        present=('Documentation = "https://docs.example.com"',),
    ),
    Customisation(
        "optional-dependencies",
        "pyproject.toml",
        (
            (
                "# template-preserve:dependencies:end\n",
                '# template-preserve:dependencies:end\n\n[project.optional-dependencies]\nmcp = ["fastmcp>=2"]\n',
            ),
        ),
        present=("[project.optional-dependencies]", 'mcp = ["fastmcp>=2"]'),
    ),
    Customisation(
        "default-groups",
        "pyproject.toml",
        (
            ("dev = []", "dev = []\nmcp = []"),
            (
                'default-groups = ["maintain", "ci", "dev", "local"]',
                'default-groups = ["maintain", "ci", "dev", "local", "mcp"]',
            ),
        ),
        present=('default-groups = ["maintain", "ci", "dev", "local", "mcp"]',),
    ),
    Customisation(
        "uv-settings",
        "pyproject.toml",
        (("[tool.uv]\n", "[tool.uv]\npackage = true\n"),),
        present=("package = true",),
    ),
    Customisation(
        "ruff-ignore",
        "pyproject.toml",
        (('    "RUF012",', '    "T201",    # a CLI prints its output\n    "RUF012",'),),
        present=('"T201",    # a CLI prints its output',),
    ),
    Customisation(
        "ruff-per-file-ignores",
        "pyproject.toml",
        (("[tool.ruff.lint.per-file-ignores]\n", '[tool.ruff.lint.per-file-ignores]\n"scripts/**" = ["INP001"]\n'),),
        present=('"scripts/**" = ["INP001"]',),
    ),
    Customisation(
        "pytest-marker",
        "pyproject.toml",
        (("markers = [\n", 'markers = [\n    "integration: needs network",\n'),),
        present=('"integration: needs network"',),
    ),
    Customisation(
        "poe-test-filter",
        "pyproject.toml",
        (("test = \"pytest -m 'not slow'\"", "test = \"pytest -m 'not slow and not integration'\""),),
        present=("test = \"pytest -m 'not slow and not integration'\"",),
    ),
    Customisation(
        "ty-rules",
        "pyproject.toml",
        (("[tool.ty.environment]", '[tool.ty.rules]\npossibly-unresolved-reference = "error"\n\n[tool.ty.environment]'),),
        present=("[tool.ty.rules]",),
    ),
    Customisation(
        "vulture",
        "pyproject.toml",
        ((None, "\n[tool.vulture]\nmin_confidence = 80\n"),),
        present=("[tool.vulture]",),
    ),
    # --- prek.toml --------------------------------------------------------
    Customisation(
        # What `prek update` writes; the template ships every rev empty.
        "hook-revs",
        "prek.toml",
        (('rev = ""', 'rev = "v1.2.3"'),),
        absent=('rev = ""',),
    ),
    Customisation(
        "coverage-floor",
        "prek.toml",
        (("--cov-fail-under=0", "--cov-fail-under=90"),),
        present=("--cov-fail-under=90",),
    ),
    Customisation(
        "commit-msg-strict",
        "prek.toml",
        (('"--verbose",', '"--strict",\n    "--verbose",'),),
        present=('"--strict",',),
    ),
    # --- source -----------------------------------------------------------
    Customisation(
        "package-init",
        "src/test_project/__init__.py",
        ((None, '\nfrom test_project.cli import main\n\n__all__ = ["main"]\n'),),
        present=('__all__ = ["main"]',),
    ),
)


# Lost today because pyproject.toml/prek.toml are regenerated by
# `sync_marked_sections.py` (DOT-630 fixes the class). `strict` turns each entry
# into a failure the moment it starts passing, so the list cannot go stale.
KNOWN_LOSSES = frozenset(
    {
        "build-backend-window",
        "project-urls",
        "optional-dependencies",
        "default-groups",
        "uv-settings",
        "ruff-ignore",
        "ruff-per-file-ignores",
        "pytest-marker",
        "poe-test-filter",
        "ty-rules",
        "vulture",
        "hook-revs",
        "coverage-floor",
        "commit-msg-strict",
    }
)


def _params() -> list[object]:
    return [
        pytest.param(c, id=c.id, marks=pytest.mark.xfail(reason="DOT-630", strict=True))
        if c.id in KNOWN_LOSSES
        else pytest.param(c, id=c.id)
        for c in CUSTOMISATIONS
    ]


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, env=GIT_ENV)


def _customise(project: Path) -> None:
    for c in CUSTOMISATIONS:
        path = project / c.file
        text = path.read_text()
        for anchor, replacement in c.edits:
            if anchor is None:
                text += replacement
                continue
            # A missing anchor means the baseline render changed shape; fail loudly
            # rather than test a customisation that was never applied.
            assert anchor in text, f"{c.id}: anchor {anchor!r} not in {c.file} at {BASELINE_TAG}"
            text = text.replace(anchor, replacement)
        path.write_text(text)


@pytest.fixture(scope="module")
def updated_project(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, subprocess.CompletedProcess[str]]:
    if _run(["git", "rev-parse", "--verify", BASELINE_TAG], REPO_ROOT).returncode != 0:
        pytest.skip(f"{BASELINE_TAG} tag not available in this checkout (shallow clone?)")

    project = tmp_path_factory.mktemp("downstream") / "proj"
    copy = ["copier", "copy", "--trust", "--skip-tasks", "-f", "-r", BASELINE_TAG, str(REPO_ROOT), str(project)]
    for key, value in ANSWERS.items():
        copy.extend(["-d", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    result = _run(copy, REPO_ROOT)
    assert result.returncode == 0, f"copier copy at {BASELINE_TAG} failed: {result.stderr}"

    _customise(project)
    for cmd in (
        ["git", "init", "-q", "-b", "main"],
        ["git", "add", "-A"],
        ["git", "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "customised"],
    ):
        assert _run(cmd, project).returncode == 0, f"{cmd} failed"

    # The core of `poe update-template`, tasks included: the tasks are where
    # `sync_marked_sections.py` rewrites pyproject.toml and prek.toml.
    update = _run(["copier", "update", "--trust", "--skip-answered", "--defaults", "--conflict", "rej", "--vcs-ref", "HEAD"], project)
    return project, update


@pytest.mark.slow
def test_update_succeeds(updated_project: tuple[Path, subprocess.CompletedProcess[str]]) -> None:
    _, update = updated_project
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"


@pytest.mark.slow
@pytest.mark.xfail(
    reason="DOT-630: copier replays the edit to src/<pkg>/__init__.py, a _skip_if_exists file, and rejects it",
    strict=True,
)
def test_update_leaves_no_rej_files(updated_project: tuple[Path, subprocess.CompletedProcess[str]]) -> None:
    project, _ = updated_project
    rejects = sorted(str(p.relative_to(project)) for p in project.rglob("*.rej") if ".venv" not in p.parts)
    assert not rejects, f"update could not apply cleanly: {rejects}"


@pytest.mark.slow
@pytest.mark.parametrize("customisation", _params())
def test_update_keeps_customisation(updated_project: tuple[Path, subprocess.CompletedProcess[str]], customisation: Customisation) -> None:
    project, _ = updated_project
    text = (project / customisation.file).read_text()
    lost = [s for s in customisation.present if s not in text]
    reverted = [s for s in customisation.absent if s in text]
    assert not lost, f"{customisation.file}: update dropped {lost}"
    assert not reverted, f"{customisation.file}: update brought back {reverted}"
