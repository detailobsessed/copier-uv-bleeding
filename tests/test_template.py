"""Comprehensive tests for copier template generation."""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import tomllib
from typing import TYPE_CHECKING, ClassVar

import pytest
from conftest import REPO_ROOT, generate_project

if TYPE_CHECKING:
    from pathlib import Path


class TestProjectTypes:
    """Test project types (app = CLI, lib = no CLI)."""

    def test_app_type_has_cli(self, copier_defaults: dict, project_factory) -> None:
        """App type should have CLI entry point."""
        project = project_factory(copier_defaults, "app")

        pyproject = project / "pyproject.toml"
        assert pyproject.exists()

        content = pyproject.read_text()
        assert "[project.scripts]" in content
        assert "test-project" in content  # CLI name from slugified project_name

    def test_lib_type_no_cli(self, copier_defaults: dict, project_factory) -> None:
        """Library type should not have CLI entry point."""
        project = project_factory(copier_defaults, "lib")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[project.scripts]" not in content

    def test_no_main_py(self, copier_defaults: dict, project_factory) -> None:
        """Neither type should generate main.py (users create their own)."""
        for project_type in ("app", "lib"):
            project = project_factory(copier_defaults, project_type)
            assert not (project / "main.py").exists()


class TestCoreFiles:
    """Test core files are generated correctly."""

    def test_pyproject_toml_exists(self, copier_defaults: dict, project_factory) -> None:
        """pyproject.toml should exist."""
        project = project_factory(copier_defaults)
        assert (project / "pyproject.toml").exists()

    def test_precommit_config_exists(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should exist."""
        project = project_factory(copier_defaults)
        assert (project / "prek.toml").exists()

    def test_ruff_config_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Ruff config should be in pyproject.toml."""
        project = project_factory(copier_defaults)
        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.ruff]" in content
        assert "[tool.ruff.lint]" in content

    def test_src_directory_exists(self, copier_defaults: dict, project_factory) -> None:
        """src directory should exist."""
        project = project_factory(copier_defaults)
        assert (project / "src").is_dir()

    def test_tests_directory_has_placeholder(self, copier_defaults: dict, project_factory) -> None:
        """tests/ ships with a placeholder so the first commit doesn't fail on pytest exit 5.

        Both `app` and `lib` project types must get the placeholder -- there's no
        conditional `_exclude`, so a missing file in either would be a regression.
        """
        for project_type in ("app", "lib"):
            project = project_factory(copier_defaults, project_type)
            tests_dir = project / "tests"
            assert tests_dir.is_dir(), f"tests/ missing for {project_type} project"
            assert (tests_dir / "__init__.py").exists(), f"tests/__init__.py missing for {project_type}"
            # python_package_import_name = "Test Project" | slugify("_") = "test_project"
            placeholder = tests_dir / "test_test_project.py"
            assert placeholder.exists(), f"placeholder test missing for {project_type}"
            content = placeholder.read_text()
            assert "import test_project" in content
            assert "def test_" in content


class TestCIConfiguration:
    """Test CI configuration options."""

    def test_ci_enabled_creates_workflow(self, copier_defaults: dict, project_factory) -> None:
        """CI enabled should create workflow file."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)
        assert (project / ".github" / "workflows" / "ci.yml").exists()

    def test_ci_disabled_no_workflow(self, copier_defaults: dict, project_factory) -> None:
        """CI disabled should not create workflow file."""
        answers = {**copier_defaults, "use_ci": False}
        project = project_factory(answers)
        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_semantic_release_creates_workflow(self, copier_defaults: dict, project_factory) -> None:
        """Semantic release enabled should create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)
        assert (project / ".github" / "workflows" / "release.yml").exists()

    def test_semantic_release_disabled_no_workflow(self, copier_defaults: dict, project_factory) -> None:
        """Semantic release disabled should not create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": False}
        project = project_factory(answers)
        assert not (project / ".github" / "workflows" / "release.yml").exists()


class TestPythonVersion:
    """Test Python version configuration."""

    def test_requires_python_314(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should require Python 3.14+."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'requires-python = ">=3.14"' in content

    def test_ruff_target_py314(self, copier_defaults: dict, project_factory) -> None:
        """Ruff should target Python 3.14."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'target-version = "py314"' in content


class TestPreCommitConfig:
    """Test pre-commit configuration."""

    def test_prek_version(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should pin prek to 0.3.11+ (provides --repo-exclude-tag)."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert 'minimum_prek_version = "0.3.11"' in content

    def test_has_betterleaks(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should have betterleaks."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "betterleaks" in content

    def test_has_betterleaks_config(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should have a .betterleaks.toml config file."""
        project = project_factory(copier_defaults)

        config = project / ".betterleaks.toml"
        assert config.exists()
        content = config.read_text()
        assert "[[allowlists]]" in content

    def test_no_pyupgrade(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should not have pyupgrade (replaced by ruff UP)."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "pyupgrade" not in content

    def test_rev_lines_have_no_trailing_comment(self, copier_defaults: dict, project_factory) -> None:
        """Every `rev` line must be matchable by sync-with-uv (DOT-603).

        sync-with-uv matches revs with a regex anchored at end-of-line, so a
        trailing comment makes the line unmatchable. The hook then matches zero
        revs and reports success, silently doing nothing forever. This is the
        regex from sync_with_uv.py verbatim, so this test fails for the same
        reason the real hook would go quiet.
        """
        repo_rev_re = re.compile(r"""^\s*rev\s*=\s*(['"])([^'"]*)\1\s*$""")
        project = project_factory(copier_defaults)

        rev_lines = [line for line in (project / "prek.toml").read_text().splitlines() if re.match(r"^\s*rev\s*=", line)]
        assert rev_lines, "expected prek.toml to declare at least one rev"

        unmatched = [line for line in rev_lines if not repo_rev_re.match(line)]
        assert not unmatched, (
            "these rev lines are invisible to sync-with-uv, which would silently "
            f"stop syncing hook versions with uv.lock: {unmatched!r}. Put per-repo "
            "notes on the line above the rev, not after it."
        )

    def test_typos_hook_does_not_write_changes(self, copier_defaults: dict, project_factory) -> None:
        """The typos hook must report, not rewrite files in place (DOT-604).

        Upstream ships `args = ["--write-changes", "--force-exclude"]`. Left at
        the default it edits files, and has corrupted hex identifiers (Mongo
        ObjectIds, git SHAs) that it read as misspelled prose. Config `args`
        replace the upstream list rather than appending, so the override must
        also re-supply `--force-exclude` or _typos.toml stops being honoured
        when prek passes explicit staged filenames.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        typos = [hook for repo in data["repos"] for hook in repo.get("hooks", []) if hook["id"] == "typos"]
        assert typos, "expected a typos hook in prek.toml"

        for hook in typos:
            args = hook.get("args")
            assert args is not None, (
                "typos must override args; the upstream default includes --write-changes, which rewrites files in place."
            )
            assert "--write-changes" not in args, f"typos must not run with --write-changes; got {args!r}"
            assert "--force-exclude" in args, (
                f"keep --force-exclude so _typos.toml exclusions still apply when prek passes explicit filenames; got {args!r}"
            )

    def test_has_typos_config(self, copier_defaults: dict, project_factory) -> None:
        """Generated project ships a _typos.toml excluding generated files (DOT-604).

        Release tooling writes abbreviated git SHAs into CHANGELOG.md, which
        typos reads as prose.
        """
        project = project_factory(copier_defaults)

        config = project / "_typos.toml"
        assert config.exists(), "generated project should ship a _typos.toml"

        with config.open("rb") as f:
            data = tomllib.load(f)

        excluded = data["files"]["extend-exclude"]
        assert "CHANGELOG.md" in excluded
        assert "uv.lock" in excluded


class TestHookProfiles:
    """use_heavy_hooks gates slow git hooks; fast hooks stay always-on."""

    @staticmethod
    def _hook_ids(project: Path) -> list[str]:
        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)
        return [hook["id"] for repo in data["repos"] for hook in repo.get("hooks", [])]

    def test_heavy_hooks_include_coverage(self, copier_defaults: dict, project_factory) -> None:
        """use_heavy_hooks=true runs coverage as a git hook."""
        ids = self._hook_ids(project_factory({**copier_defaults, "use_heavy_hooks": True}))
        assert "pytest-cov" in ids

    def test_light_hooks_are_the_default(self, copier_defaults: dict, project_factory) -> None:
        """The default profile (heavy hooks off) drops coverage but keeps the fast hooks."""
        ids = self._hook_ids(project_factory(copier_defaults))
        assert "pytest-cov" not in ids
        for fast in ("ruff", "ty", "pytest-testmon"):
            assert fast in ids, f"{fast} should stay always-on"

    def test_conventional_commit_gated_on_semantic_release(self, copier_defaults: dict, project_factory) -> None:
        """conventional-pre-commit ships only with semantic-release, and without --strict."""
        with_release = project_factory({**copier_defaults, "use_semantic_release": True})
        assert "conventional-pre-commit" in self._hook_ids(with_release)
        assert "--strict" not in (with_release / "prek.toml").read_text()

        without_release = project_factory({
            **copier_defaults,
            "use_ci": False,
            "use_semantic_release": False,
        })
        assert "conventional-pre-commit" not in self._hook_ids(without_release)


class TestDependencies:
    """Test dependency configuration."""

    def test_no_yore_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should not have yore dependency."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "yore" not in content

    def test_no_tomli_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should not have tomli dependency."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tomli" not in content

    def test_prek_version_updated(self, copier_defaults: dict, project_factory) -> None:
        """prek dependency should be >= 0.3.11 (introduces --repo-exclude-tag, used by scripts/prek-autoupdate.sh)."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"prek>=0.3.11"' in content


class TestCIWorkflows:
    """Test CI workflow configuration (from smoke_test.sh assertions)."""

    def test_ci_has_setup_uv(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow should use setup-uv action."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        content = ci_yml.read_text()
        assert "astral-sh/setup-uv" in content

    def test_ci_poe_tasks_exist_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """All poe tasks referenced in CI workflow should exist in pyproject.toml."""
        import re

        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        pyproject = project / "pyproject.toml"

        ci_content = ci_yml.read_text()
        pyproject_content = pyproject.read_text()

        # Find all poe task references in CI (e.g., "uv run poe check", "uv run poe docs-build")
        poe_tasks = re.findall(r"uv run poe ([\w-]+)", ci_content)

        # Verify each task exists in pyproject.toml
        for task in poe_tasks:
            assert "[tool.poe.tasks]" in pyproject_content, "pyproject.toml should have poe tasks"
            # Check task is defined (as string, array, or dotted table like check.parallel)
            assert f"{task} = " in pyproject_content or f"{task} = [" in pyproject_content or f"{task}." in pyproject_content, (
                f"poe task '{task}' referenced in CI but not defined in pyproject.toml"
            )

    def test_release_has_semantic_release(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use semantic-release."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "semantic-release" in content

    def test_release_checks_out_main(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should checkout main explicitly (workflow_run defaults to PR branch)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "ref: main" in content

    def test_release_has_uv_publish(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use uv publish in separate pypi-publish job."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "uv publish" in content

    def test_release_setup_uv_has_github_token(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow setup-uv steps should have github-token to avoid rate limiting (#237)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "github-token:" in content

    def test_release_setup_uv_has_github_token_no_pypi(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow release job setup-uv should have github-token even without pypi-publish job (#237)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": False}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "github-token:" in content

    def test_ci_setup_uv_has_github_token(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow setup-uv steps should have github-token to avoid rate limiting (#237)."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "github-token:" in content

    def test_ci_has_prek_action(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow should use prek-action for comprehensive quality checks."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "j178/prek-action" in content

    def test_ci_prek_skips_redundant_hooks(self, copier_defaults: dict, project_factory) -> None:
        """CI prek job should skip hooks redundant with dedicated CI jobs."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "SKIP: pytest-testmon,uv-lock" in content
        # `no-commit-to-main` was removed from the template (DOT-541) — must not reappear in SKIP.
        assert "no-commit-to-main" not in content, (
            "CI workflow still references `no-commit-to-main` in SKIP — the hook was removed "
            "from prek.toml (DOT-541), so this entry must go too."
        )

    def test_ci_prek_refreshes_lockfile(self, copier_defaults: dict, project_factory) -> None:
        """CI prek job should refresh the lockfile before running hooks."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "run: uv lock\n" in content
        lock_idx = content.index("run: uv lock")
        prek_idx = content.index("j178/prek-action")
        assert lock_idx < prek_idx

    def test_pyproject_has_build_system(self, copier_defaults: dict, project_factory) -> None:
        """pyproject.toml should have build-system section."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[build-system]" in content

    def test_uv_build_has_upper_bound(self, copier_defaults: dict, project_factory) -> None:
        """`build-system.requires` must pin `uv_build` with an upper bound (DOT-589).

        An unbounded `uv_build` makes uv print a noisy warning on every `uv sync`
        / `uv build` (drowns out real warnings) and risks silent sdist breakage
        when `uv_build` ships a future major. The template ships with
        `uv_build>=0.9,<0.12`; bump the upper bound when uv_build crosses 0.12+.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)

        requires = data["build-system"]["requires"]
        uv_build_specs = [r for r in requires if r.startswith(("uv_build", "uv-build"))]
        assert uv_build_specs, f"build-system.requires must list uv_build; got {requires!r}"

        spec = uv_build_specs[0]
        # Reject bare "uv_build" or specs without an upper bound. The point of
        # the pin is to keep a future breaking release from being auto-picked
        # by the build frontend — so an upper bound (`<` or `<=`) is required.
        assert "<" in spec, (
            f"uv_build must have an upper version bound to avoid the uv warning and "
            f"to prevent silent breakage on a future major release. Got {spec!r}; "
            f"expected something like 'uv_build>=0.9,<0.12'."
        )

    def test_pypi_false_excludes_classifiers_and_keywords(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, classifiers and keywords should not be in pyproject.toml."""
        answers = {**copier_defaults, "publish_to_pypi": False}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_pypi_true_includes_classifiers_and_keywords(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, classifiers and keywords should be in pyproject.toml."""
        answers = {**copier_defaults, "publish_to_pypi": True}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" in content
        assert "keywords" in content

    def test_pypi_true_has_environment(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, release workflow should have environment: pypi."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "name: pypi" in content

    def test_pypi_false_no_environment(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, release workflow should not have environment: pypi."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": False}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "name: pypi" not in content

    def test_pypi_false_no_readme_badge(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, README should not have PyPI badge (#165)."""
        answers = {**copier_defaults, "publish_to_pypi": False}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pypi.org/project/" not in content

    def test_pypi_true_has_readme_badge(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, README should have PyPI badge."""
        answers = {**copier_defaults, "publish_to_pypi": True}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pypi.org/project/" in content


class TestCascadingBooleanDefaults:
    """Test that boolean question defaults cascade correctly when parent questions are disabled.

    Regression tests for https://github.com/detailobsessed/copier-uv-bleeding/issues/45
    When use_ci=false, downstream questions (use_semantic_release, publish_to_pypi,
    use_blacksmith_runners) should all default to false since their 'when' conditions
    prevent them from being asked.
    """

    def test_use_ci_false_no_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false (without explicit publish_to_pypi), classifiers should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        # Remove keys that should cascade from use_ci
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_use_ci_false_no_release_workflow(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, release.yml should not be created."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "release.yml").exists()
        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_use_ci_false_no_pypi_environment(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, no PyPI-related config should appear in release workflow."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        # No release workflow at all
        assert not (project / ".github" / "workflows" / "release.yml").exists()

    def test_use_ci_false_no_matrix_in_nonexistent_ci(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, CI workflow should not exist (no matrix testing)."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_use_ci_true_defaults_include_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=true with defaults, classifiers should appear (positive case)."""
        answers = {
            **copier_defaults,
            "use_ci": True,
        }
        # Remove to let them cascade from use_ci=true → default true
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" in content
        assert "keywords" in content

    def test_use_ci_true_defaults_create_all_workflows(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=true with defaults, both CI and release workflows should exist."""
        answers = {
            **copier_defaults,
            "use_ci": True,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert (project / ".github" / "workflows" / "ci.yml").exists()
        assert (project / ".github" / "workflows" / "release.yml").exists()

    def test_use_semantic_release_false_no_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=false, publish_to_pypi should cascade to false."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": False,
        }
        answers.pop("publish_to_pypi", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_use_ci_false_no_semantic_release_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, semantic_release config and maintain group should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" not in content
        assert "python-semantic-release" not in content
        assert "maintain" not in content

    def test_use_semantic_release_false_no_semantic_release_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=false explicitly, semantic_release config should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": False,
        }
        answers.pop("publish_to_pypi", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" not in content
        assert "python-semantic-release" not in content
        assert "maintain" not in content

    def test_changelog_file_under_changelog_not_default_templates(self, copier_defaults: dict, project_factory) -> None:
        """changelog_file should be under [tool.semantic_release.changelog], not default_templates (#261)."""
        answers = {**copier_defaults, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert 'changelog_file = "CHANGELOG.md"' in content
        assert "[tool.semantic_release.changelog.default_templates]" not in content

    def test_use_semantic_release_true_has_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=true, semantic_release config and maintain group should appear."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": True,
        }
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" in content
        assert "python-semantic-release" in content
        assert "maintain" in content


class TestTemplateCleanup:
    """Test removal of overly specific config and proper gating of platform-specific tasks.

    Regression tests for #49 (docs-deploy) and #50 (coverage.paths, ty.src.exclude).
    """

    def test_no_coverage_paths(self, copier_defaults: dict, project_factory) -> None:
        """Generated pyproject.toml should not have [tool.coverage.paths]."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.coverage.paths]" not in content

    def test_coverage_excludes_main_guard(self, copier_defaults: dict, project_factory) -> None:
        """Coverage exclude_lines should include if __name__ == '__main__' (#57)."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "if __name__ == .__main__." in content

    def test_description_with_quotes(self, copier_defaults: dict, project_factory) -> None:
        """Project description containing double quotes should produce valid TOML."""
        answers = {**copier_defaults, "project_description": 'Helps you "close the loop"'}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        assert data["project"]["description"] == 'Helps you "close the loop"'

    def test_no_ty_src_exclude_fixtures(self, copier_defaults: dict, project_factory) -> None:
        """Generated pyproject.toml should not have ty.src.exclude for fixtures."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tests/fixtures" not in content

    def test_github_has_gh_cli_tasks(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should have gh CLI poe tasks."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "gh release list" in content
        assert "gh run list" in content
        assert "gh run watch" in content


class TestTemplateUpdateCheck:
    """Test template update check hook and related tasks (#161)."""

    def test_check_template_update_script_exists(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have check-template-update.sh hook adapter."""
        project = project_factory(copier_defaults)

        script = project / "scripts" / "check-template-update.sh"
        assert script.exists()
        content = script.read_text()
        assert "copier check-update" in content

    def test_post_checkout_in_hook_types(self, copier_defaults: dict, project_factory) -> None:
        """prek.toml should install post-checkout hooks."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        with config.open("rb") as f:
            data = tomllib.load(f)
        assert "post-checkout" in data["default_install_hook_types"]

    def test_check_template_update_hook_exists(self, copier_defaults: dict, project_factory) -> None:
        """prek.toml should have check-template-update hook."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "check-template-update" in content

    def test_check_template_poe_task(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have check-template poe task that calls copier check-update."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "copier check-update" in content
        assert "check-template" in content

    def test_update_template_poe_task(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have update-template poe task that chains uv sync --upgrade and prek autoupdate."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "update-template" in content
        assert "copier update" in content
        # update-template must pass both:
        #   --defaults    → don't prompt on newly-added questions; use their defaults.
        #                   Required so the task survives non-TTY contexts (CI, scripted
        #                   runs, agent sessions); otherwise copier crashes inside
        #                   questionary trying to open a prompt. DOT-542 originally banned
        #                   this flag under the wrong premise that it caused pyproject.toml
        #                   clobbering — verified: clobbering is driven by copier's 3-way
        #                   merge engine, not by --defaults, which only governs questions.
        #   --conflict rej → separate .rej files instead of inline conflict markers in
        #                    working files, so the user sees what copier couldn't apply.
        assert "--defaults" in content
        assert "--conflict rej" in content
        assert "uv sync --upgrade" in content
        assert "scripts/prek-autoupdate.sh" in content
        assert (project / "scripts" / "prek-autoupdate.sh").exists()

    def test_lychee_rev_is_pinned_not_empty(self, copier_defaults: dict, project_factory) -> None:
        """Lychee should have a pinned rev (not empty) since its 'nightly' tag is mutable."""
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)
        lychee_repos = [r for r in data["repos"] if r.get("repo", "").endswith("/lychee")]
        assert len(lychee_repos) == 1, "Expected exactly one lychee repo entry"
        rev = lychee_repos[0]["rev"]
        assert rev, "Lychee rev should be pinned, not empty"
        assert rev.startswith("lychee-v"), f"Lychee rev should be a versioned tag, got: {rev}"

    def test_prek_autoupdate_script_has_lychee_workaround(self, copier_defaults: dict, project_factory) -> None:
        """scripts/prek-autoupdate.sh wraps `prek autoupdate` with the lychee `nightly` workaround (DOT-492, DOT-540).

        Verifies the script exists, is executable, and uses prek 0.3.11+ `--repo-exclude-tag` to
        prevent lychee's `rev` from flipping to `nightly` (which lychee's own hook then rejects).
        Tracks lycheeverse/lychee#1601 — remove the flag once upstream closes that issue (DOT-504).
        """
        project = project_factory(copier_defaults)

        script = project / "scripts" / "prek-autoupdate.sh"
        assert script.exists(), "prek-autoupdate.sh must ship in the scaffolded project"
        assert os.access(script, os.X_OK), "prek-autoupdate.sh must be executable"

        body = script.read_text()
        assert "prek autoupdate" in body, "script must invoke `prek autoupdate`"
        assert "--repo-exclude-tag https://github.com/lycheeverse/lychee=nightly" in body, (
            "script must exclude the lychee `nightly` tag so prek picks the latest versioned tag"
        )

    def test_check_merge_conflict_has_assume_in_merge(self, copier_defaults: dict, project_factory) -> None:
        """check-merge-conflict must pass --assume-in-merge so it catches markers from `copier update --conflict inline` (DOT-542).

        Without --assume-in-merge, pre-commit-hooks' check-merge-conflict only fires when git
        records a pending merge (.git/MERGE_MSG). `copier update` doesn't set that state, so the
        default-args form silently misses inline conflict markers produced by Copier.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        builtin = next(r for r in data["repos"] if r.get("repo") == "builtin")
        hook = next(h for h in builtin["hooks"] if h["id"] == "check-merge-conflict")
        assert hook.get("args") == ["--assume-in-merge"], (
            f"check-merge-conflict must pass --assume-in-merge for copier update conflicts; got {hook.get('args')!r}"
        )

    def test_no_copier_rej_files_hook(self, copier_defaults: dict, project_factory) -> None:
        """A local prek hook must block commits containing copier update .rej files (DOT-542).

        Since `update-template` now uses `--conflict rej`, an unresolved conflict produces a
        `<file>.rej` artifact. Committing those would leave the project half-merged. This hook
        enforces manual review by failing on any staged path matching `\\.rej$`.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        local_repos = [r for r in data["repos"] if r.get("repo") == "local"]
        hooks = [h for repo in local_repos for h in repo.get("hooks", [])]
        rej_hook = next((h for h in hooks if h["id"] == "no-copier-rej-files"), None)
        assert rej_hook is not None, "Expected a local 'no-copier-rej-files' hook in prek.toml"
        assert rej_hook["language"] == "fail", "Hook must use language='fail' so any matching file fails the run"
        assert rej_hook["files"] == r"\.rej$", f"Hook must target .rej files; got {rej_hook['files']!r}"

    def test_uv_sync_task_runs_in_copier_temp_render_dirs(self) -> None:
        """`uv sync --upgrade` must run in copier's temp render dirs, skip destination on update.

        Regression guard for DOT-587 (deleted uv.lock) and DOT-588 (broken .venv).

        Background: on `copier update`, copier renders OLD and NEW template versions into temp
        dirs (`copier._main.old_copy.*` / `copier._main.new_copy.*`), then deletes from the
        destination anything present in old_copy but absent in new_copy (`_remove_old_files`).

        Old template versions (≤0.34.3) ran an unguarded `uv sync` in `_tasks`, so old_copy
        ends up with `uv.lock` and a full `.venv/` tree. If NEW's task skips uv sync in
        new_copy (via a naive `[ -d .git ]` guard — temp dirs have no .git), copier sees those
        entries as "removed" and wipes the user's real `uv.lock` and `.venv`.

        The fix is the inverted guard: run in temp dirs and on `copy`, skip in destination
        during update (`poe update-template` handles destination explicitly). This test pins
        the guard so it cannot regress back to `[ -d .git ]` without an explicit decision.
        """
        copier_yml = pathlib.Path(__file__).resolve().parent.parent / "copier.yml"
        content = copier_yml.read_text()

        # The uv sync task must use the inverted guard: skip destination, run in temp dirs.
        assert "[ ! -d .git ]; then uv sync --upgrade" in content, (
            "copier.yml _tasks must run `uv sync --upgrade` in copier's temp render dirs "
            "(no .git) AND on `copy`, but skip the destination during update. "
            "Reverting to `[ -d .git ]` would re-introduce DOT-587 (deleted uv.lock) and "
            "DOT-588 (broken .venv)."
        )

        # The opposite — `[ -d .git ]; then uv sync` — must NOT be present. (Substring match
        # is intentional; rules out the naive guard even if other text wraps it.)
        assert "[ -d .git ]; then uv sync --upgrade" not in content, (
            "copier.yml _tasks has `[ -d .git ]; then uv sync --upgrade` — the naive guard "
            "that lets copier delete the user's uv.lock and .venv on update. Use "
            "`[ ! -d .git ]` instead (see DOT-587 / DOT-588)."
        )

    def test_update_banner_does_not_claim_deps_synced(self) -> None:
        """The `🎉 Template updated!` banner must not claim "Dependencies synced" (DOT-587 fix follow-up).

        With the inverted `uv sync` guard (see test_uv_sync_task_runs_in_copier_temp_render_dirs),
        copier's _tasks no longer run uv sync in the destination during update. The poe
        `update-template` chain runs `uv sync --upgrade` after copier returns. So the banner
        — which fires from copier's _tasks before the poe chain finishes — would be lying
        if it claimed deps were already synced.
        """
        copier_yml = pathlib.Path(__file__).resolve().parent.parent / "copier.yml"
        # Pull just the line(s) containing the update banner's printf, so this only
        # inspects the user-visible string and isn't tripped by explanatory comments.
        banner_lines = [line for line in copier_yml.read_text().splitlines() if "🎉 Template updated!" in line]
        assert banner_lines, "Update banner missing from copier.yml"
        banner = "\n".join(banner_lines)

        assert "Dependencies synced" not in banner, (
            f"Update banner claims `Dependencies synced` — but copier's _tasks skip "
            f"`uv sync` in the destination during update (see DOT-587). The poe "
            f"`update-template` chain syncs deps AFTER this banner. Drop the line.\n"
            f"Banner:\n{banner}"
        )

    def test_no_commit_to_main_hook_absent(self, copier_defaults: dict, project_factory) -> None:
        """The `no-commit-to-main` pre-push hook must not ship in prek.toml (DOT-541).

        Solo workflows commit straight to main for trivial / safe changes (typo fixes, doc
        tweaks, dep bumps). The template used to ship a `no-commit-to-main` pre-push hook
        that blocked that workflow unconditionally, forcing every change through a PR even
        when there was no reviewer to wait for. The template no longer ships it; users who
        want PR-only enforcement can add a six-line local hook themselves.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        all_hook_ids = [h["id"] for repo in data["repos"] for h in repo.get("hooks", [])]
        assert "no-commit-to-main" not in all_hook_ids, (
            f"prek.toml ships a `no-commit-to-main` hook — the template was changed to drop it "
            f"(DOT-541) so solo workflows can commit straight to main. Current hooks: {all_hook_ids!r}"
        )


class TestTemplateUpdateNotification:
    """Test the post-checkout hook adapter (check-template-update.sh) behavior."""

    SCRIPT_SRC = pathlib.Path(__file__).resolve().parent.parent / "project" / "scripts" / "check-template-update.sh"

    @classmethod
    def _setup(cls, tmp_path: Path) -> Path:
        """Create a minimal directory with the script."""
        project = tmp_path / "project"
        scripts = project / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy2(cls.SCRIPT_SRC, scripts / "check-template-update.sh")
        return project

    @staticmethod
    def _run(project: Path, *, args: list[str] | None = None) -> subprocess.CompletedProcess:
        """Run check-template-update.sh."""
        script = project / "scripts" / "check-template-update.sh"
        cmd = ["bash", str(script), *(args or [])]
        return subprocess.run(cmd, cwd=project, capture_output=True, text=True, check=False, start_new_session=True)

    def test_file_level_restore_skipped(self, tmp_path: Path) -> None:
        """Script exits silently when git signals file-level restore (arg3=0)."""
        project = self._setup(tmp_path)
        result = self._run(project, args=["oldref", "newref", "0"])
        assert result.returncode == 0
        assert not result.stdout
        assert not result.stderr


class TestGitLabSupport:
    """Test GitLab repository provider support.

    Regression tests for #51 (GitHub-specific files) and #52 (GitLab support).
    """

    def test_gitlab_no_github_directory(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have .github/ directory."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        assert not (project / ".github").exists()

    def test_gitlab_has_gitlab_ci(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects with CI should have .gitlab-ci.yml."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com", "use_ci": True}
        project = project_factory(answers)

        assert (project / ".gitlab-ci.yml").exists()
        content = (project / ".gitlab-ci.yml").read_text()
        assert "quality" in content
        assert "test" in content

    def test_gitlab_no_ci_no_gitlab_ci(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects without CI should not have .gitlab-ci.yml."""
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".gitlab-ci.yml").exists()
        assert not (project / ".github").exists()

    def test_gitlab_no_actionlint_in_precommit(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have actionlint pre-commit hook."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        config = project / "prek.toml"
        content = config.read_text()
        assert "actionlint" not in content

    def test_gitlab_precommit_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """GitLab prek.toml should be valid TOML with expected repos."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        config = project / "prek.toml"
        with config.open("rb") as f:
            data = tomllib.load(f)
        repo_urls = [r["repo"] for r in data["repos"]]
        assert "https://github.com/crate-ci/typos" in repo_urls

    def test_gitlab_no_gh_cli_tasks(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have gh CLI poe tasks."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "gh release list" not in content
        assert "gh run list" not in content
        assert "docs-deploy" not in content

    def test_gitlab_no_discussions_url(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have Discussions URL."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "Discussions" not in content

    def test_gitlab_has_pipeline_badge(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have pipeline badge in README."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pipeline" in content
        assert "gitlab.com" in content

    def test_gitlab_has_gitlab_urls(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have gitlab.com URLs in pyproject.toml."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "gitlab.com" in content

    def test_gitlab_semantic_release_remote(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have [tool.semantic_release.remote] with type=gitlab (#236)."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com", "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" in content
        assert 'type = "gitlab"' in content
        assert "domain" not in content

    def test_gitlab_selfhosted_semantic_release_remote_domain(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should include domain in semantic_release.remote (#236)."""
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
            "use_ci": True,
            "use_semantic_release": True,
        }
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" in content
        assert 'type = "gitlab"' in content
        assert 'domain = "gitlab.company.com"' in content

    def test_github_no_semantic_release_remote(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should NOT have [tool.semantic_release.remote] section."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" not in content

    def test_github_still_has_github_directory(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should still have .github/ directory (positive case)."""
        project = project_factory(copier_defaults)

        assert (project / ".github").exists()
        assert not (project / ".gitlab-ci.yml").exists()


class TestCLIFramework:
    """Test app project type scaffolding."""

    def test_app_type_no_scaffold_code(self, copier_defaults: dict, project_factory) -> None:
        """App type should not generate scaffold source files (users create their own via uv init).

        Note: ``tests/__init__.py`` and ``tests/test_<package>.py`` ARE generated as
        a placeholder so the first commit doesn't fail the pytest-testmon hook.
        See test_tests_directory_has_placeholder.
        """
        project = project_factory(copier_defaults, "app")
        assert not (project / "src" / "test_project" / "_internal").exists()
        assert not (project / "src" / "test_project" / "__main__.py").exists()
        assert not (project / "src" / "test_project" / "py.typed").exists()
        assert not (project / "tests" / "test_cli.py").exists()
        assert not (project / "tests" / "test_api.py").exists()
        assert not (project / "tests" / "conftest.py").exists()


class TestOpenSource:
    """``open_source`` gates LICENSE + community-health files.

    When ``open_source`` is false (internal/private), the LICENSE, community-health
    files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, issue/PR templates, FUNDING) and
    the license/Funding metadata in ``pyproject.toml`` are all omitted.
    """

    COMMUNITY_FILES: ClassVar[list[str]] = [
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        ".github/FUNDING.yml",
        ".github/pull_request_template.md",
    ]

    def test_open_source_has_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects ship all community-health files and a LICENSE."""
        project = project_factory({**copier_defaults, "open_source": True})
        for f in self.COMMUNITY_FILES:
            assert (project / f).exists(), f"{f} should exist for open-source projects"
        assert (project / ".github" / "ISSUE_TEMPLATE").exists()

    def test_internal_no_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects ship none of the community-health files or LICENSE."""
        project = project_factory({**copier_defaults, "open_source": False})
        for f in self.COMMUNITY_FILES:
            assert not (project / f).exists(), f"{f} should NOT exist for internal projects"
        assert not (project / ".github" / "ISSUE_TEMPLATE").exists()

    # -- pyproject.toml license + funding metadata --

    def test_internal_no_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have license metadata in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / "pyproject.toml").read_text()
        assert "license = " not in content
        assert "license-files" not in content

    def test_open_source_has_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects should have license metadata in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / "pyproject.toml").read_text()
        assert 'license = "MIT"' in content
        assert "license-files" in content

    def test_internal_no_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have a Funding URL in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / "pyproject.toml").read_text()
        assert "Funding" not in content
        assert "sponsors" not in content

    def test_open_source_has_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Open-source GitHub projects should have a Funding URL in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / "pyproject.toml").read_text()
        assert "Funding" in content

    # -- Core files always present --

    def test_internal_still_has_core_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should still have core project files."""
        project = project_factory({**copier_defaults, "open_source": False})
        assert (project / "pyproject.toml").exists()
        assert (project / "README.md").exists()
        assert (project / "CHANGELOG.md").exists()
        assert (project / "prek.toml").exists()
        assert (project / ".editorconfig").exists()
        assert (project / "src").is_dir()

    def test_internal_pyproject_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects pyproject.toml should be valid TOML."""
        project = project_factory({**copier_defaults, "open_source": False})
        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "project" in data

    # -- Lychee config --

    def test_internal_lychee_accepts_401(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should accept 401 for auth-gated URLs."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / ".lychee.toml").read_text()
        assert "401" in content

    def test_open_source_lychee_no_401(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects .lychee.toml should not accept 401."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / ".lychee.toml").read_text()
        assert "401" not in content

    def test_internal_lychee_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should be valid TOML."""
        project = project_factory({**copier_defaults, "open_source": False})
        with (project / ".lychee.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "accept" in data

    # -- Self-hosted repository URLs --

    def test_selfhosted_pyproject_urls(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should use repository_host for URLs."""
        answers = {
            **copier_defaults,
            "open_source": False,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
        }
        project = project_factory(answers)
        content = (project / "pyproject.toml").read_text()
        assert "gitlab.company.com" in content
        assert "://gitlab.com/" not in content


class TestOpenSourceMigration:
    """The 0.41.0 `_migrations` step derives `open_source` from the legacy
    `project_visibility` / `project_audience` answers.

    Without this migration, `copier update --defaults` resolves `open_source`
    from its own schema default (`repository_provider == 'github.com'`) instead
    of the project's real history, silently flipping visibility for any project
    whose history disagrees with that default — e.g. an internal project hosted
    on GitHub gains a LICENSE and community-health files with no `.rej` warning.

    A full `copier update` end-to-end run can't exercise this migration in this
    test suite: `_migrations` are gated by PEP 440 version comparison against the
    *tagged* template version, and an unreleased commit always resolves to a dev
    version below the next tag (verified manually against a temporary local
    `0.41.0` tag during development). So this tests the migration script directly.
    """

    SCRIPT: ClassVar[pathlib.Path] = REPO_ROOT / "migrations" / "0.41.0_open_source.py"

    def test_migration_registered_in_copier_yml(self) -> None:
        """copier.yml's `_migrations` entry must reference the script that actually exists."""
        content = (REPO_ROOT / "copier.yml").read_text()
        assert "migrations/0.41.0_open_source.py" in content
        assert self.SCRIPT.is_file(), f"{self.SCRIPT} referenced in copier.yml but missing"

    def _run(self, tmp_path: pathlib.Path, answers_body: str) -> str:
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(answers_body)
        result = subprocess.run(
            ["python3", str(self.SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"migration script failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        return answers_file.read_text()

    def test_derives_open_source_true_from_public_visibility(self, tmp_path: Path) -> None:
        """An internal-on-paper GitHub project isn't affected, but a public project must stay public."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nproject_visibility: public\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_derives_open_source_false_from_internal_visibility(self, tmp_path: Path) -> None:
        """The exact regression this migration exists for: an internal GitHub project must not
        silently become open-source (schema default is `repository_provider == 'github.com'`)."""
        result = self._run(tmp_path, "repository_provider: github.com\nproject_visibility: internal\n")
        assert re.search(r"^open_source:\s*false\s*$", result, re.MULTILINE), result

    def test_falls_back_to_project_audience_when_visibility_absent(self, tmp_path: Path) -> None:
        """Very old projects (pre-project_visibility) only have project_audience recorded."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nproject_audience: public-oss\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_leaves_existing_open_source_answer_untouched(self, tmp_path: Path) -> None:
        """If `open_source` is already answered, the migration must not override it."""
        result = self._run(tmp_path, "project_visibility: public\nopen_source: false\n")
        assert re.search(r"^open_source:\s*false\s*$", result, re.MULTILINE), result

    def test_noop_without_any_legacy_answer(self, tmp_path: Path) -> None:
        """No legacy keys to derive from — leave the file alone and let the question's own default apply."""
        original = "repository_provider: gitlab.com\n"
        result = self._run(tmp_path, original)
        assert result == original

    def test_falls_back_to_community_health_files_when_visibility_and_audience_absent(self, tmp_path: Path) -> None:
        """Projects from before project_visibility existed only have use_community_health_files."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nuse_community_health_files: true\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_derives_open_source_when_visibility_and_community_health_agree(self, tmp_path: Path) -> None:
        """The common case: use_community_health_files matches its project_visibility-derived default."""
        result = self._run(tmp_path, "project_visibility: public\nuse_community_health_files: true\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_abstains_when_visibility_and_community_health_disagree(self, tmp_path: Path) -> None:
        """A public project with community files explicitly turned off (DOT-599 review finding):
        no single boolean preserves both axes, so the migration must not guess."""
        original = "project_visibility: public\nuse_community_health_files: false\n"
        result = self._run(tmp_path, original)
        assert result == original
        assert "open_source" not in result


class TestMarkedSectionsSync:
    """`_tasks` step (see copier.yml) that replaces `copier update`'s fuzzy-patch
    handling of `pyproject.toml`/`prek.toml` with a regenerate-and-preserve
    approach (DOT-599): the whole file is rendered fresh from the template on
    every update, except for regions wrapped in
    `# template-preserve:&lt;name&gt;:start`/`:end` comments in the .jinja source,
    which are copied verbatim from the previous version.

    Both files moved to `_skip_if_exists`, so this script is the *only* thing
    that updates them after first generation.
    """

    SCRIPT: ClassVar[pathlib.Path] = REPO_ROOT / "migrations" / "sync_marked_sections.py"

    @staticmethod
    def _load_module():
        import importlib.util

        spec = importlib.util.spec_from_file_location("sync_marked_sections", TestMarkedSectionsSync.SCRIPT)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_script_referenced_in_copier_yml(self) -> None:
        content = (REPO_ROOT / "copier.yml").read_text()
        assert "migrations/sync_marked_sections.py" in content
        assert self.SCRIPT.is_file(), f"{self.SCRIPT} referenced in copier.yml but missing"

    def test_pyproject_and_prek_toml_in_skip_if_exists(self) -> None:
        """The whole mechanism depends on Copier's default patch-based update
        never touching these files — otherwise both it and this script would
        race to write them."""
        content = (REPO_ROOT / "copier.yml").read_text()
        skip_block = content.split("_skip_if_exists:")[1].split("_exclude:")[0]
        assert "pyproject.toml" in skip_block
        assert "prek.toml" in skip_block

    def test_unmarked_content_always_reflects_fresh_render(self) -> None:
        module = self._load_module()
        existing = "line-length = 100\n"
        new = "line-length = 140\n"
        assert module.sync_text(existing, new) == new

    def test_marked_region_preserved_verbatim(self) -> None:
        module = self._load_module()
        existing = 'a\n# template-preserve:deps:start\ndependencies = ["requests>=2"]\n# template-preserve:deps:end\nb\n'
        new = "a2\n# template-preserve:deps:start\ndependencies = []\n# template-preserve:deps:end\nb2\n"
        merged = module.sync_text(existing, new)
        assert 'dependencies = ["requests>=2"]' in merged
        assert "a2" in merged
        assert "b2" in merged

    def test_reordered_markers_match_by_name_not_position(self) -> None:
        """The bug found in Templator's own implementation (positional
        matching): a release that reorders marked regions must not splice
        content into the wrong slot."""
        module = self._load_module()
        existing = (
            "# template-preserve:foo:start\nFOO-OLD\n# template-preserve:foo:end\n"
            "# template-preserve:bar:start\nBAR-OLD\n# template-preserve:bar:end\n"
        )
        new = (
            "# template-preserve:bar:start\nBAR-DEFAULT\n# template-preserve:bar:end\n"
            "# template-preserve:foo:start\nFOO-DEFAULT\n# template-preserve:foo:end\n"
        )
        merged = module.sync_text(existing, new)
        assert "FOO-OLD" in merged
        assert "BAR-OLD" in merged
        foo_pos = merged.index("FOO-OLD")
        bar_pos = merged.index("BAR-OLD")
        assert bar_pos < foo_pos  # bar block comes first in `new`, and must keep its own content

    def test_never_seen_marker_keeps_fresh_default_instead_of_emptying(self) -> None:
        """The footgun found in Templator's own implementation: a marked
        region with no snapshot (new to this release, or never customized)
        must keep the fresh render's own default, not go blank."""
        module = self._load_module()
        existing = "x\n"  # no markers at all yet
        new = "# template-preserve:newthing:start\nDEFAULT-CONTENT\n# template-preserve:newthing:end\n"
        merged = module.sync_text(existing, new)
        assert "DEFAULT-CONTENT" in merged

    def test_markers_present_in_pyproject_template(self) -> None:
        content = (REPO_ROOT / "project" / "pyproject.toml.jinja").read_text()
        for name in ("dependencies", "project-scripts", "dependency-groups", "tool-uv-index", "extra-poe-tasks"):
            assert f"# template-preserve:{name}:start" in content, f"missing marker: {name}"
            assert f"# template-preserve:{name}:end" in content, f"missing marker: {name}"

    def test_markers_present_in_prek_template(self) -> None:
        content = (REPO_ROOT / "project" / "prek.toml.jinja").read_text()
        assert "# template-preserve:extra-local-hooks:start" in content
        assert "# template-preserve:extra-local-hooks:end" in content

    def test_legacy_bootstrap_preserves_data_on_first_marker_aware_update(self) -> None:
        """The critical regression caught in review (Macroscope, PR #329): a
        project generated *before* markers existed has none of the
        `# template-preserve:*` comments. Without bootstrapping, its first
        update to a marker-aware template version would silently replace
        every now-marked region with the fresh render's bare default,
        discarding real user data with zero warning — the exact class of bug
        DOT-599 was filed for, reintroduced by the fix meant to prevent it."""
        module = self._load_module()
        legacy_pyproject = (
            '[project]\nname = "x"\ndependencies = ["requests>=2.31", "pydantic>=2"]\n\n'
            '[project.scripts]\nmytool = "mytool.cli:main"\n\n'
            '[dependency-groups]\nci = ["ruff>=0.14"]\ndev = ["ipython"]\n\n'
            '[[tool.uv.index]]\nurl = "https://custom.example.com"\n\n'
            '[tool.poe.tasks]\nsetup = "uv sync"\nlint = "ruff check ."\n'
            'serve = "python -m mytool.server"\nwatch = "gh run watch"\n'
        )
        fresh = (
            '[project]\nname = "x"\n# template-preserve:dependencies:start\ndependencies = []\n'
            "# template-preserve:dependencies:end\n\n"
            "# template-preserve:project-scripts:start\n[project.scripts]\n"
            'mytool = "mytool.cli:main"\n# template-preserve:project-scripts:end\n\n'
            "# template-preserve:dependency-groups:start\n[dependency-groups]\n"
            'ci = ["ruff>=0.15"]\ndev = []\n# template-preserve:dependency-groups:end\n\n'
            "# template-preserve:tool-uv-index:start\n# template-preserve:tool-uv-index:end\n\n"
            '[tool.poe.tasks]\nsetup = "uv sync"\nlint = "ruff check ."\nwatch = "gh run watch"\n'
            "# template-preserve:extra-poe-tasks:start\n# template-preserve:extra-poe-tasks:end\n"
        )
        merged = module.sync_text(legacy_pyproject, fresh)

        import tomllib

        tomllib.loads(merged)  # must stay valid TOML
        assert '"requests>=2.31"' in merged
        assert "pydantic" in merged
        assert "custom.example.com" in merged
        assert 'serve = "python -m mytool.server"' in merged
        assert merged.count("serve = ") == 1  # moved, not duplicated

    def test_legacy_bootstrap_preserves_custom_local_hook(self) -> None:
        module = self._load_module()
        legacy_prek = (
            '[[repos]]\nrepo = "local"\n\n'
            '[[repos.hooks]]\nid = "ty"\nname = "ty type checker"\n\n'
            '[[repos.hooks]]\nid = "my-custom-check"\nname = "my custom check"\n'
            'entry = "scripts/custom-check.sh"\n\n'
            '[[repos.hooks]]\nid = "check-template-update"\nname = "check for template updates"\n'
        )
        fresh = (
            '[[repos]]\nrepo = "local"\n\n'
            '[[repos.hooks]]\nid = "ty"\nname = "ty type checker"\n\n'
            '[[repos.hooks]]\nid = "check-template-update"\nname = "check for template updates"\n\n'
            "# template-preserve:extra-local-hooks:start\n# template-preserve:extra-local-hooks:end\n"
        )
        merged = module.sync_text(legacy_prek, fresh)

        import tomllib

        tomllib.loads(merged)
        assert "my-custom-check" in merged
        assert "custom-check.sh" in merged
        assert merged.count("my-custom-check") == 1


class TestMcpRegistry:
    """Test publish_to_mcp_registry question gates MCP registry publishing workflow.

    When publish_to_mcp_registry=true (requires use_semantic_release=true),
    a standalone mcp-registry-publish.yml workflow should be generated and the
    release.yml should include an mcp-registry-publish job.
    """

    def test_mcp_registry_workflow_exists_when_enabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=true should generate mcp-registry-publish.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": True}
        project = project_factory(answers)

        assert (project / ".github" / "workflows" / "mcp-registry-publish.yml").exists()

    def test_mcp_registry_workflow_absent_when_disabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=false should not generate mcp-registry-publish.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": False}
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "mcp-registry-publish.yml").exists()

    def test_release_yml_has_mcp_job_when_enabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=true should add mcp-registry-publish job to release.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "mcp-registry-publish" in content
        assert "mcp-registry-publish.yml" in content

    def test_release_yml_no_mcp_job_when_disabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=false should not add mcp-registry-publish job to release.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": False}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "mcp-registry-publish" not in content


class TestSkipIfExists:
    """Test _skip_if_exists preserves user changes across copier recopy.

    Uses copier recopy to simulate template re-application without needing
    a version difference. copier recopy is more aggressive than copier update
    (no 3-way merge), so if _skip_if_exists works here, it works everywhere.
    """

    @pytest.mark.slow
    def test_recopy_preserves_modified_readme(self, tmp_path: Path, copier_defaults: dict) -> None:
        """User-modified README.md should not be overwritten (core _skip_if_exists file)."""
        project = generate_project(tmp_path, copier_defaults)

        readme = project / "README.md"
        assert readme.exists()

        # User customizes README
        readme.write_text("# My Project\n\nCustom README content.\n")

        # Re-apply template
        result = subprocess.run(
            ["copier", "recopy", "--trust", "--skip-tasks", "-r", "HEAD", "--skip-answered", "--defaults", "--overwrite"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"copier recopy failed: {result.stderr}"

        content = readme.read_text()
        assert "Custom README content" in content, f"README.md was overwritten by copier recopy. Content:\n{content}"


class TestIntegration:
    """Integration tests that run uv sync and checks on generated project."""

    @staticmethod
    def _init_git_repo(project: Path) -> None:
        """Initialize a git repo with an initial commit in the given project."""
        subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: Initial commit"],
            cwd=project,
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@test.com",
            },
        )

    @pytest.mark.slow
    def test_uv_sync_succeeds(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should successfully run uv sync."""
        project = generate_project(tmp_path, copier_defaults)
        self._init_git_repo(project)

        # Run uv sync
        result = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"uv sync failed: {result.stderr}"

    @pytest.mark.slow
    def test_first_commit_succeeds_with_prek_hooks(self, tmp_path: Path, copier_defaults: dict) -> None:
        """First `git commit` on a freshly scaffolded project must succeed.

        Reproduces the exact user flow from a fresh folder:
            copier copy ... && cd <dest>
            uv sync
            git init && uv run prek install && bash scripts/prek-autoupdate.sh
            git add -A && git commit -m "feat: init commit"

        Originally added as a regression test for DOT-491 (pytest-testmon hook exited 5
        because the template shipped no tests/). Intentionally runs the FULL prek hook
        chain with no SKIP -- if any hook fails on a freshly scaffolded project, the
        template is broken from the user's perspective and we have work to do.
        """
        project = generate_project(tmp_path, copier_defaults)

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

        git_env: dict[str, str] = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@test.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@test.com",
        }
        # An ambient SKIP=... in the developer's shell or CI step would silently
        # disable prek hooks and defeat the whole point of this regression test.
        git_env.pop("SKIP", None)

        subprocess.run(
            ["git", "init", "--initial-branch=main"],
            cwd=project,
            check=True,
            capture_output=True,
        )
        install = subprocess.run(
            ["uv", "run", "prek", "install"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert install.returncode == 0, f"prek install failed: {install.stderr}"
        autoupdate = subprocess.run(
            ["bash", "scripts/prek-autoupdate.sh"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert autoupdate.returncode == 0, f"prek-autoupdate.sh failed: {autoupdate.stderr}"

        # Mirror the real user flow: hooks may auto-fix files (formatters, lockfile sync)
        # on the first run, abort the commit, and the user re-stages and retries.
        # Allow up to 2 attempts; the second must succeed.
        for attempt in (1, 2):
            subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
            commit = subprocess.run(
                ["git", "commit", "-m", "feat: init commit"],
                cwd=project,
                capture_output=True,
                text=True,
                check=False,
                env=git_env,
            )
            if commit.returncode == 0:
                break
            assert attempt == 1, (
                f"first commit on freshly scaffolded project failed after re-stage:\nstdout:\n{commit.stdout}\nstderr:\n{commit.stderr}"
            )

    @pytest.mark.slow
    def test_update_preserves_uv_lock_and_venv_across_versions(self, tmp_path: Path, copier_defaults: dict) -> None:
        """`copier update` from an old template version must not delete the user's `uv.lock` or trash `.venv` (DOT-587, DOT-588).

        Regression scenario:
          - User's project was scaffolded on template ≤0.34.3, which ran an unguarded
            `uv sync` in `_tasks`. So copier's `old_copy` temp render produces `uv.lock` and
            a full `.venv/` tree.
          - On update to a fixed template, copier compares `old_copy` vs `new_copy` and
            removes from the destination anything present only in old_copy. Without the
            inverted-guard fix (see `test_uv_sync_task_runs_in_copier_temp_render_dirs`),
            new_copy lacks both → `uv.lock` is deleted and `.venv` is mauled.

        This test runs the full flow against the real 0.34.3 tag and the current HEAD,
        skipping if the tag is absent (e.g. shallow clones in CI).
        """
        repo_root = pathlib.Path(__file__).resolve().parent.parent

        # Need the 0.34.3 tag to render the "old" baseline. Skip if a shallow clone is
        # missing it rather than fail spuriously.
        tag_check = subprocess.run(
            ["git", "rev-parse", "--verify", "0.34.3"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if tag_check.returncode != 0:
            pytest.skip("0.34.3 tag not available in this checkout (shallow clone?)")

        project = tmp_path / "proj"

        # Render at 0.34.3, the version with the unguarded `uv sync` task. `--skip-tasks`
        # because we'll set up the venv ourselves in a controlled way below.
        cmd = [
            "copier",
            "copy",
            "--trust",
            "--skip-tasks",
            "-f",
            "-r",
            "0.34.3",
            str(repo_root),
            str(project),
        ]
        defaults = {**copier_defaults, "project_type": "app"}
        for k, v in defaults.items():
            cmd.extend(["-d", f"{k}={str(v).lower() if isinstance(v, bool) else v}"])
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"copier copy at 0.34.3 failed: {result.stderr}"

        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
        subprocess.run(["git", "add", "-A"], cwd=project, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=project, env=git_env, check=True)

        # Populate the user's local state: real `uv.lock` and `.venv` from `uv sync`.
        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed during setup: {sync.stderr}"
        assert (project / "uv.lock").is_file(), "Setup precondition: uv.lock should exist after uv sync"
        assert (project / ".venv" / "pyvenv.cfg").is_file(), "Setup precondition: .venv/pyvenv.cfg should exist after uv sync"
        subprocess.run(["git", "add", "uv.lock"], cwd=project, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "add uv.lock", "--no-verify"],
            cwd=project,
            env=git_env,
            check=False,
        )

        # Run the update against current HEAD (which must contain the fix).
        update = subprocess.run(
            ["copier", "update", "--trust", "--defaults", "--conflict", "rej", "--vcs-ref", "HEAD"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"

        # Core assertions — both files must survive the update.
        assert (project / "uv.lock").is_file(), (
            "uv.lock was deleted by `copier update` — DOT-587 regression. Check the `uv sync` task guard in copier.yml _tasks."
        )
        assert (project / ".venv" / "pyvenv.cfg").is_file(), (
            ".venv/pyvenv.cfg disappeared after `copier update` — DOT-588 regression. "
            "`uv sync` in the destination's venv would now error with "
            "'cannot be recreated because it is not a virtual environment'."
        )

    @pytest.mark.slow
    def test_semantic_release_writes_gitlab_urls_for_selfhosted(self, tmp_path: Path, copier_defaults: dict) -> None:
        """semantic-release must write GitLab-format commit URLs into CHANGELOG.md when `repository_provider=gitlab.com` (DOT-590).

        Static config tests (`test_gitlab_semantic_release_remote`,
        `test_gitlab_selfhosted_semantic_release_remote_domain`) cover the rendered TOML, but
        they don't catch the case where python-semantic-release ignores or misinterprets the
        config and falls back to GitHub URL conventions — exactly the symptom the user saw
        (their existing CHANGELOG had `github.com/<namespace>/<pkg>/commit/<sha>` for a GitLab
        project). This is the end-to-end check: actually run `semantic-release changelog` on
        a multi-level GitLab self-hosted setup and verify the URL format.
        """
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.pnet.ch",
            "repository_namespace": "kop/ismar",
            "project_name": "Die Zeit",
            "open_source": False,
        }
        project = generate_project(tmp_path, answers)

        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "git@gitlab.pnet.ch:kop/ismar/die-zeit.git"],
            cwd=project,
            check=True,
        )
        subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "feat: initial commit", "--no-verify"],
            cwd=project,
            env=git_env,
            check=True,
        )

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

        # Make a real feat commit so semantic-release has something to changelog.
        (project / "foo.txt").write_text("x\n")
        subprocess.run(["git", "add", "foo.txt"], cwd=project, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "feat: add foo", "--no-verify"],
            cwd=project,
            env=git_env,
            check=True,
        )

        result = subprocess.run(
            ["uv", "run", "semantic-release", "changelog"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"semantic-release changelog failed: {result.stderr}"

        changelog = (project / "CHANGELOG.md").read_text()

        # Positive: at least one correctly-formatted gitlab self-hosted commit URL exists.
        assert "https://gitlab.pnet.ch/kop/ismar/die-zeit/-/commit/" in changelog, (
            f"Expected gitlab self-hosted commit URL in CHANGELOG.md. Got:\n{changelog}"
        )

        # Negative: no github.com URLs leaked into the gitlab project's changelog (DOT-590).
        assert "github.com" not in changelog, f"github.com URL leaked into a gitlab project's CHANGELOG.md (DOT-590):\n{changelog}"

        # Negative: no underscore form of the repo slug (the user's specific symptom — `die_zeit`
        # instead of `die-zeit`). semantic-release should derive the slug from the git remote
        # URL, never from python_package_import_name.
        assert "die_zeit" not in changelog, (
            f"Underscored repo slug `die_zeit` leaked into CHANGELOG.md — semantic-release "
            f"appears to be using python_package_import_name instead of the repo slug:\n{changelog}"
        )
