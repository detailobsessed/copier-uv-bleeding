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
        "use_docs": True,
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
    if result.returncode != 0:
        pytest.fail(f"Copier failed: {result.stderr}")

    return tmp_path


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
