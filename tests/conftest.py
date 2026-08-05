"""Shared fixtures for copier template tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture
def copier_defaults() -> dict:
    """Default answers for copier prompts."""
    return {
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
    }


def generate_project(
    tmp_path: Path,
    answers: dict,
    project_type: str = "app",
) -> Path:
    """Generate a project using copier.

    IMPORTANT: We use ``-r HEAD`` to test against the current commit, not the latest
    git tag.  Copier resolves ``copier.yml`` (questions, defaults, ``_exclude`` patterns)
    from the checked-out VCS ref — *not* from the working directory.  Dirty template
    files under ``project/`` are overlaid automatically, but ``copier.yml`` itself is
    read from the ref.  Without ``-r HEAD``, tests would silently run against the last
    *tagged* release and miss any uncommitted configuration changes.

    We use ``--skip-tasks`` to prevent copier's ``_tasks`` (which include ``uv sync
    --upgrade``) from running on every generated project.  Those tasks require Python
    3.14 and network access; skipping them keeps the test suite fast and portable.
    The ``TestIntegration`` tests explicitly call ``uv sync`` where needed.
    """
    answers = {**answers, "project_type": project_type}

    cmd = [
        "copier",
        "copy",
        "--trust",
        "--skip-tasks",
        "-f",
        "-r",
        "HEAD",
        str(REPO_ROOT),
        str(tmp_path),
    ]

    for key, value in answers.items():
        if isinstance(value, bool):
            cmd.extend(["-d", f"{key}={str(value).lower()}"])
        else:
            cmd.extend(["-d", f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 and not _is_temp_clone_cleanup_failure(result.stderr, tmp_path):
        pytest.fail(f"Copier failed: {result.stderr}")

    return tmp_path


def _is_temp_clone_cleanup_failure(stderr: str, dst: Path) -> bool:
    """True if copier rendered successfully but crashed clearing its own temp clone (DOT-606).

    On a dirty working tree copier takes its dirty-file overlay path, which does extra git
    work inside the temp clone it made of this repo. Something still holds a handle under
    that clone's `.git` when `_cleanup` calls `rmtree(..., ignore_errors=False)`, so copier
    exits non-zero *after* every file has been written. Observed on macOS with copier 9.17.x.

    The effect is a test suite that is green in CI (which always checks out clean) and red
    for anyone mid-change — with the failure landing on whichever test happens to render
    first, so it reads as flakiness rather than as one deterministic bug. Re-running the
    "failed" test alone usually passes, which sends triage down the wrong path entirely.

    Deliberately narrow. This tolerates only an `rmtree` of a path copier itself names
    `copier._vcs.clone.*`, and only when the destination actually received a rendered
    project. A render that genuinely failed leaves no `pyproject.toml`, and any other
    non-zero exit still fails the test with copier's own stderr.
    """
    if "copier._vcs.clone" not in stderr:
        return False
    if not any(marker in stderr for marker in ("Directory not empty", "rmtree", "Errno 66")):
        return False
    return (dst / "pyproject.toml").is_file()


def _cache_key(answers: dict, project_type: str) -> str:
    """Create a stable cache key from answers dict and project type."""
    merged = {**answers, "project_type": project_type}
    return str(sorted(merged.items()))


@pytest.fixture(scope="module")
def project_factory(tmp_path_factory: pytest.TempPathFactory):
    """Module-scoped factory that caches copier generations by answer key.

    Tests sharing the same answer set reuse a single generated project instead of
    invoking ``copier copy`` for each test.  All consuming tests MUST be read-only —
    they may read files but must not modify the generated project directory.
    """
    cache: dict[str, Path] = {}

    def _generate(answers: dict, project_type: str = "app") -> Path:
        key = _cache_key(answers, project_type)
        if key not in cache:
            path = tmp_path_factory.mktemp("project")
            cache[key] = generate_project(path, answers, project_type)
        return cache[key]

    return _generate
