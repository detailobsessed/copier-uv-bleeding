"""Shared fixtures for copier template tests."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent

# The one copier failure the suite tolerates (DOT-606), matched as a whole rather than as
# loose substrings. The `OSError` line must itself name a path under copier's own temp
# clone: a render error's traceback also mentions that directory — every template frame
# lives inside it — so `"copier._vcs.clone" in stderr` is nearly vacuous on its own.
_CLONE_CLEANUP_RE = re.compile(
    r"^OSError: \[Errno \d+\] Directory not empty: .*copier\._vcs\.clone\.",
    re.MULTILINE,
)

# ...and it must have been raised *by* the cleanup, not merely alongside it.
_CLEANUP_FRAME = ", in _cleanup"

# A chained traceback means something failed first and the cleanup crash rode along on the
# unwind. That is the dangerous shape: a partial render whose exception is followed by the
# cleanup `OSError`, which would otherwise satisfy every check above.
_CHAINED_EXCEPTION_MARKERS = (
    "During handling of the above exception",
    "The above exception was the direct cause",
)


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

    Deliberately narrow, because this is the one place a real copier failure could be
    swallowed. All four must hold:

    1. The final exception is an `OSError` naming a path under copier's own temp clone.
    2. It was raised from a `_cleanup` frame — the cleanup is what failed, not something
       that merely happened to mention the same directory.
    3. Nothing failed before it. A chained traceback is exactly how a partial render would
       present: its own exception, then the cleanup `OSError` raised while unwinding.
    4. The destination actually received a render.

    Independent substring checks are not enough for (1) and (2): every template frame in a
    Jinja render error lives *inside* the temp clone, so a genuine render failure can put
    `copier._vcs.clone` and `rmtree` in stderr on unrelated lines while `pyproject.toml` —
    written early — already exists in the destination. Any other non-zero exit still fails
    the test with copier's own stderr.

    If copier renames `_cleanup`, this stops matching and DOT-606's dirty-tree failures
    come back visibly. That is the intended direction to fail in.
    """
    if not _CLONE_CLEANUP_RE.search(stderr):
        return False
    if _CLEANUP_FRAME not in stderr:
        return False
    if any(marker in stderr for marker in _CHAINED_EXCEPTION_MARKERS):
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
