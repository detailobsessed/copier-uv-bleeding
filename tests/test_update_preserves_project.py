"""A real `copier update` must never undo what a downstream project changed.

Every customisation below was lost by an actual update of an actual project
(DOT-620 and its comments): from 0.41.0 to 0.41.14 a task regenerated
pyproject.toml and prek.toml on every update and kept only marked regions.
Unit tests on that task covered one key at a time and passed while those
updates went out, so this test runs the user's flow end to end instead:
generate at a released tag, customise the way a project does, commit,
`copier update` to HEAD with its tasks, then check each
customisation on its own so a failure names the loss.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent

# The release the reporting project was on before its last destructive update.
BASELINE_TAG = "0.41.14"

# `copier_defaults` is function-scoped, so the module fixtures below cannot use it.
BASE_ANSWERS = {
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
    "project_type": "app",
}

# `use_heavy_hooks` puts the pytest-cov hook (and its `--cov-fail-under`) in prek.toml.
ANSWERS = {**BASE_ANSWERS, "use_heavy_hooks": True}

# Answer sets the customised project does not cover: a lib without releases (the
# `update-template` line and the end of prek.toml render differently), and
# GitLab with a custom index (`[[tool.uv.index]]` only renders with one).
PRISTINE_VARIANTS = {
    "lib-no-release": {**BASE_ANSWERS, "project_type": "lib", "use_ci": False, "use_semantic_release": False},
    "gitlab-custom-index": {
        **BASE_ANSWERS,
        "repository_provider": "gitlab.com",
        "open_source": False,
        "use_custom_pypi_index": True,
        # A reachable index: copier's `uv sync` task runs in its temp renders.
        "custom_pypi_index_url": "https://pypi.org/simple",
    },
}

# Asked at BASELINE_TAG, gone at HEAD (DOT-676).
REMOVED_QUESTIONS = {"use_ci", "use_heavy_hooks", "configure_repo_settings", "use_custom_pypi_index"}

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}

# What `poe update-template` runs.
UPDATE = ["copier", "update", "--trust", "--skip-answered", "--defaults", "--conflict", "inline", "--vcs-ref", "HEAD"]

# A project's first update past 0.41.14 runs the task it already has, which still
# passes `--conflict rej`; the switch to inline only lands with that update.
UPDATE_FROM_0_41 = [arg if arg != "inline" else "rej" for arg in UPDATE]

# The 3.15 release deletes template lines directly beside customisations, a one-time
# cost (docs/update.md): `requires-python` moved above `readme`, leaving the old line
# right above every released project's `version`, and the `# template-preserve:*`
# comments went from around `dependencies`, the project's own poe tasks and its own
# local hooks. Each entry is one conflict block: lines that must appear in it.
EXPECTED_CONFLICTS = {
    "pyproject.toml": [
        # Both sides moved the window off 0.12; a project that bumped uv first sees this.
        ('"uv_build>=0.13,<0.14"', '"uv_build>=0.13.4,<0.14"'),
        ('requires-python = ">=3.14"', 'version = "0.18.0"', 'dependencies = ["httpx>=0.28"]'),
        ('serve = "python -m test_project.server"', 'upgrade = { shell = "uv sync --upgrade && uv run prek update" }'),
    ],
    "prek.toml": [
        # The pytest-cov hook went with `use_heavy_hooks` (DOT-676); a project that tuned
        # it keeps its version beside the deletion and decides.
        ('id = "pytest-cov"', "--cov-fail-under=90"),
        ('id = "check-schema"',),
    ],
}
# The new `requires-python` line has nothing beside it to collide with.
EXPECTED_MERGED = 'requires-python = ">=3.15"\nreadme = "README.md"\n<<<<<<< before updating\n'


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
        (("\n[project.urls]\n", '\n[project.optional-dependencies]\nmcp = ["fastmcp>=2"]\n\n[project.urls]\n'),),
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
        # Inside the inert "extra poe tasks" markers, where 0.41.x told projects
        # to put them; the update changes `update-template` three lines above.
        "own-poe-task",
        "pyproject.toml",
        (
            (
                "# template-preserve:extra-poe-tasks:end\n",
                'serve = "python -m test_project.server"\n# template-preserve:extra-poe-tasks:end\n',
            ),
        ),
        present=('serve = "python -m test_project.server"',),
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
        # What `prek update` writes; the template ships every rev empty and never
        # touches those lines, so the project's revs replay cleanly.
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
    Customisation(
        "own-local-hook",
        "prek.toml",
        (
            (
                "# template-preserve:extra-local-hooks:end\n",
                (
                    "\n[[repos.hooks]]\n"
                    'id = "check-schema"\n'
                    'name = "check schema"\n'
                    'entry = "uv run python scripts/check_schema.py"\n'
                    'language = "system"\n'
                    "pass_filenames = false\n"
                    "# template-preserve:extra-local-hooks:end\n"
                ),
            ),
        ),
        present=('id = "check-schema"',),
    ),
    # --- source -----------------------------------------------------------
    Customisation(
        "package-init",
        "src/test_project/__init__.py",
        ((None, '\nfrom test_project.cli import main\n\n__all__ = ["main"]\n'),),
        present=('__all__ = ["main"]',),
    ),
)


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


def _generate_and_update(
    project: Path,
    answers: dict,
    *,
    customise: bool,
    update: list[str] = UPDATE,
    before_commit: Callable[[Path], None] | None = None,
) -> subprocess.CompletedProcess[str]:
    if _run(["git", "rev-parse", "--verify", BASELINE_TAG], REPO_ROOT).returncode != 0:
        pytest.skip(f"{BASELINE_TAG} tag not available in this checkout (shallow clone?)")

    copy = ["copier", "copy", "--trust", "--skip-tasks", "-f", "-r", BASELINE_TAG, str(REPO_ROOT), str(project)]
    for key, value in answers.items():
        copy.extend(["-d", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    result = _run(copy, REPO_ROOT)
    assert result.returncode == 0, f"copier copy at {BASELINE_TAG} failed: {result.stderr}"

    if customise:
        _customise(project)
    if before_commit is not None:
        before_commit(project)
    for cmd in (
        ["git", "init", "-q", "-b", "main"],
        ["git", "add", "-A"],
        ["git", "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "baseline"],
    ):
        assert _run(cmd, project).returncode == 0, f"{cmd} failed"

    return _run(update, project)


def _conflicts(project: Path) -> list[str]:
    """Paths holding `.rej` files or inline conflict markers after the update."""
    found = []
    for path in project.rglob("*"):
        if ".venv" in path.parts or ".git" in path.parts or not path.is_file():
            continue
        if path.suffix == ".rej":
            found.append(str(path.relative_to(project)))
        elif "<<<<<<< before updating" in path.read_text(errors="replace"):
            found.append(f"{path.relative_to(project)} (conflict markers)")
    return sorted(found)


def _conflict_blocks(text: str) -> list[str]:
    """Each `<<<<<<< ... >>>>>>>` region of a file, markers included."""
    blocks, current = [], None
    for line in text.splitlines():
        if line.startswith("<<<<<<< "):
            current = [line]
        elif current is not None:
            current.append(line)
            if line.startswith(">>>>>>> "):
                blocks.append("\n".join(current))
                current = None
    return blocks


@pytest.fixture(scope="module")
def updated_project(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, subprocess.CompletedProcess[str]]:
    project = tmp_path_factory.mktemp("downstream") / "proj"
    return project, _generate_and_update(project, ANSWERS, customise=True)


@pytest.mark.slow
def test_update_succeeds(updated_project: tuple[Path, subprocess.CompletedProcess[str]]) -> None:
    _, update = updated_project
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"


@pytest.mark.slow
def test_update_conflicts_only_where_expected(updated_project: tuple[Path, subprocess.CompletedProcess[str]]) -> None:
    """Only the documented collisions may conflict; every other customisation merges cleanly."""
    project, _ = updated_project
    expected_files = sorted(f"{name} (conflict markers)" for name in EXPECTED_CONFLICTS)
    assert _conflicts(project) == expected_files, f"unexpected conflicts: {_conflicts(project)}"
    for name, expected in EXPECTED_CONFLICTS.items():
        blocks = _conflict_blocks((project / name).read_text())
        assert len(blocks) == len(expected), f"{name}: expected {len(expected)} conflicts, got:\n\n" + "\n\n".join(blocks)
        for block, lines in zip(blocks, expected, strict=True):
            missing = [line for line in lines if line not in block]
            assert not missing, f"{name}: conflict is not the expected one; missing {missing}:\n{block}"
    assert EXPECTED_MERGED in (project / "pyproject.toml").read_text(), "the new requires-python should merge in cleanly"


@pytest.mark.slow
def test_update_under_conflict_rej_loses_nothing_silently(tmp_path: Path) -> None:
    """The 0.41.x `update-template` passes `--conflict rej`; every edit it drops must sit in a `.rej`.

    Under rej, `git apply` sends every hunk whose context changed to a `.rej`
    while the file keeps the template's side. The template carries no migration
    to stop that: the `no-copier-rej-files` hook every rej-era project has blocks
    the commit, and the edits are applied by hand from the `.rej`. This pins the
    "by hand, not lost" half of that.
    """
    project = tmp_path / "proj"
    update = _generate_and_update(project, ANSWERS, customise=True, update=UPDATE_FROM_0_41)
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"
    silently_lost = []
    for customisation in CUSTOMISATIONS:
        target = project / customisation.file
        rej = target.with_name(target.name + ".rej")
        kept = target.read_text() + (rej.read_text() if rej.exists() else "")
        silently_lost += [f"{customisation.id}: {s}" for s in customisation.present if s not in kept]
    assert not silently_lost, f"edits in neither the file nor a .rej: {silently_lost}"
    assert any(project.rglob("*.rej")), "this release collides with common edits, so rej must leave .rej files"


@pytest.mark.slow
@pytest.mark.parametrize("customisation", CUSTOMISATIONS, ids=lambda c: c.id)
def test_update_keeps_customisation(updated_project: tuple[Path, subprocess.CompletedProcess[str]], customisation: Customisation) -> None:
    project, _ = updated_project
    text = (project / customisation.file).read_text()
    lost = [s for s in customisation.present if s not in text]
    reverted = [s for s in customisation.absent if s in text]
    assert not lost, f"{customisation.file}: update dropped {lost}"
    assert not reverted, f"{customisation.file}: update brought back {reverted}"


@pytest.mark.slow
def test_colliding_template_change_is_marked_not_lost(tmp_path: Path) -> None:
    """When a release changes the very line a project edited, both versions must reach the user.

    The template is a clone of HEAD with one extra commit, a fake release that moves
    the `uv_build` window the project also moved. Under `--conflict rej` the project's
    line went to a `.rej` and the file silently took the template's; inline keeps both.
    The fake window has a shape the template never ships (`<1`), so HEAD's own bumps
    never match it, yet it resolves: the update's tasks build the project.
    """
    template = tmp_path / "template"
    assert _run(["git", "clone", "-q", str(REPO_ROOT), str(template)], tmp_path).returncode == 0
    jinja = template / "project" / "pyproject.toml.jinja"
    rendered, moved = re.subn(r'"uv_build>=[^"]+"', '"uv_build>=0.13,<1"', jinja.read_text(), count=1)
    assert moved, "the template no longer pins uv_build in requires"
    jinja.write_text(rendered)
    release = ["git", "-c", "commit.gpgsign=false", "commit", "-qam", "fake release", "--no-verify"]
    assert _run(release, template).returncode == 0

    project = tmp_path / "proj"
    copy = ["copier", "copy", "--trust", "--skip-tasks", "-f", "-r", BASELINE_TAG, str(template), str(project)]
    for key, value in ANSWERS.items():
        copy.extend(["-d", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    assert _run(copy, tmp_path).returncode == 0
    pyproject = project / "pyproject.toml"
    pyproject.write_text(pyproject.read_text().replace('"uv_build>=0.12.1,<0.13"', '"uv_build>=0.13,<0.14"'))
    for cmd in (
        ["git", "init", "-q", "-b", "main"],
        ["git", "add", "-A"],
        ["git", "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "baseline"],
    ):
        assert _run(cmd, project).returncode == 0, f"{cmd} failed"

    update = _run(UPDATE, project)
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"
    text = pyproject.read_text()
    assert "<<<<<<< before updating" in text, "the collision must be marked"
    assert '"uv_build>=0.13,<0.14"' in text, "the project's version of the line was lost"
    assert '"uv_build>=0.13,<1"' in text, "the template's version of the line was lost"


@pytest.mark.slow
@pytest.mark.parametrize("answers", PRISTINE_VARIANTS.values(), ids=PRISTINE_VARIANTS.keys())
def test_pristine_update_matches_a_fresh_render(tmp_path: Path, answers: dict) -> None:
    """An untouched project must come out of the update exactly as HEAD renders it.

    Anything else is a merge artefact the project never asked for, like a conflict
    or a stray blank line.
    """
    project = tmp_path / "proj"
    update = _generate_and_update(project, answers, customise=False)
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"
    assert not _conflicts(project), f"update could not merge cleanly: {_conflicts(project)}"

    fresh = tmp_path / "fresh"
    copy = ["copier", "copy", "--trust", "--skip-tasks", "-f", "-r", "HEAD", str(REPO_ROOT), str(fresh)]
    answers = {key: value for key, value in answers.items() if key not in REMOVED_QUESTIONS}
    for key, value in answers.items():
        copy.extend(["-d", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
    assert _run(copy, REPO_ROOT).returncode == 0
    for name in ("pyproject.toml", "prek.toml"):
        assert (project / name).read_text() == (fresh / name).read_text(), f"{name} differs from a fresh render at HEAD"


@pytest.mark.slow
def test_project_without_ci_gains_ci_but_not_releases(tmp_path: Path) -> None:
    """`use_ci: false` maps onto the questions it used to hide (DOT-676).

    Such a project never stored `use_semantic_release` or `use_blacksmith_runners`,
    so `--defaults` would turn on semantic-release, PyPI publishing and runners it
    never set up. CI itself is always on now, so that part arrives.
    """
    project = tmp_path / "proj"
    update = _generate_and_update(project, PRISTINE_VARIANTS["lib-no-release"], customise=False)
    assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"
    stored = (project / ".copier-answers.yml").read_text()
    assert "use_semantic_release: false" in stored
    assert "use_blacksmith_runners: false" in stored
    assert "use_ci" not in stored, "copier drops a removed question's answer"
    assert (project / ".github" / "workflows" / "ci.yml").exists()
    assert not (project / ".github" / "workflows" / "release.yml").exists()


def _add_dependency(project: Path) -> None:
    result = _run(["uv", "add", "--no-sync", "attrs"], project)
    assert result.returncode == 0, f"uv add failed: {result.stderr}"


@pytest.mark.slow
def test_update_leaves_the_project_lock_alone(tmp_path: Path) -> None:
    """`uv.lock` belongs to the project: an update must not re-lock it (DOT-677).

    Copier runs `_tasks` in the destination before it replays the project's edits, so
    `pyproject.toml` is still the bare template render at that point. A task that may
    lock (`uv run` without `--frozen`) drops every dependency the project added, and
    `_skip_if_exists` then keeps that lock instead of the project's.
    """
    project = tmp_path / "proj"
    result = _generate_and_update(project, BASE_ANSWERS, customise=False, before_commit=_add_dependency)
    assert result.returncode == 0, result.stderr
    assert 'name = "attrs"' in (project / "uv.lock").read_text()
    assert _run(["git", "diff", "--exit-code", "--", "uv.lock"], project).returncode == 0, "the update changed uv.lock"
