"""Comprehensive tests for copier template generation."""

from __future__ import annotations

import os
import subprocess
import tomllib
from typing import TYPE_CHECKING, ClassVar

import pytest
from conftest import generate_project

if TYPE_CHECKING:
    from pathlib import Path


class TestProjectTypes:
    """Test different project types generate correctly."""

    def test_package_type_has_cli(self, copier_defaults: dict, project_factory) -> None:
        """Package type should have CLI entry point."""
        project = project_factory(copier_defaults, "package")

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

    def test_app_type_has_main(self, copier_defaults: dict, project_factory) -> None:
        """App type should have main.py."""
        project = project_factory(copier_defaults, "app")

        main_py = project / "main.py"
        assert main_py.exists()


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

    def test_tests_directory_exists(self, copier_defaults: dict, project_factory) -> None:
        """tests directory should exist."""
        project = project_factory(copier_defaults)
        assert (project / "tests").is_dir()


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
        """Pre-commit config should have correct prek version."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert 'minimum_prek_version = "0.3.2"' in content

    def test_has_gitleaks(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should have gitleaks."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "gitleaks" in content

    def test_no_pyupgrade(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should not have pyupgrade (replaced by ruff UP)."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "pyupgrade" not in content


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
        """prek dependency should be >= 0.3.1."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"prek>=0.3.1"' in content


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
            # Check task is defined (either as string or table)
            assert f"{task} = " in pyproject_content or f"{task} = [" in pyproject_content, (
                f"poe task '{task}' referenced in CI but not defined in pyproject.toml"
            )

    def test_release_has_semantic_release(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use semantic-release."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "semantic-release" in content

    def test_release_has_uv_publish(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use uv publish."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "uv publish" in content

    def test_pyproject_has_build_system(self, copier_defaults: dict, project_factory) -> None:
        """pyproject.toml should have build-system section."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[build-system]" in content

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
        assert "environment: pypi" in content

    def test_pypi_false_no_environment(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, release workflow should not have environment: pypi."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": False}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "environment: pypi" not in content


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

    def test_envrc_activates_venv(self, copier_defaults: dict, project_factory) -> None:
        """Generated .envrc should activate the uv-managed virtualenv (#59)."""
        project = project_factory(copier_defaults)

        envrc = project / ".envrc"
        content = envrc.read_text()
        assert "VIRTUAL_ENV" in content

    def test_no_ty_src_exclude_fixtures(self, copier_defaults: dict, project_factory) -> None:
        """Generated pyproject.toml should not have ty.src.exclude for fixtures."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tests/fixtures" not in content

    def test_github_has_docs_deploy(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should have docs-deploy poe task."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "docs-deploy" in content
        assert "gh-deploy" in content

    def test_github_has_gh_cli_tasks(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should have gh CLI poe tasks."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "gh release list" in content
        assert "gh run list" in content
        assert "gh run watch" in content


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
        assert "pages" in content

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

    def test_gitlab_no_giscus(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have Giscus comments."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        comments = project / "docs" / ".overrides" / "partials" / "comments.html"
        content = comments.read_text()
        assert "giscus" not in content

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
        assert "gitlab.io" in content

    def test_github_still_has_github_directory(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should still have .github/ directory (positive case)."""
        project = project_factory(copier_defaults)

        assert (project / ".github").exists()
        assert not (project / ".gitlab-ci.yml").exists()


class TestTyperOption:
    """Test typer CLI option."""

    def test_typer_enabled_has_typer_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Typer enabled should add typer dependency."""
        answers = {**copier_defaults, "use_typer": True}
        project = project_factory(answers, "package")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"typer>=' in content

    def test_typer_disabled_no_typer_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Typer disabled should not add typer dependency."""
        answers = {**copier_defaults, "use_typer": False}
        project = project_factory(answers, "package")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "typer" not in content

    def test_typer_enabled_uses_typer_in_cli(self, copier_defaults: dict, project_factory) -> None:
        """Typer enabled should use typer in cli.py."""
        answers = {**copier_defaults, "use_typer": True}
        project = project_factory(answers, "package")

        cli_py = project / "src" / "test_project" / "_internal" / "cli.py"
        content = cli_py.read_text()
        assert "import typer" in content
        assert "app = typer.Typer" in content


class TestProjectVisibility:
    """Test project_visibility question gates open-source scaffolding.

    When project_visibility=internal, community files (LICENSE, CODE_OF_CONDUCT,
    CONTRIBUTING, SECURITY) and their docs counterparts should be excluded.
    pyproject.toml should omit license metadata and Funding URL.
    mkdocs.yml should omit community pages from nav.
    """

    # -- Files that should be EXCLUDED for internal projects --

    COMMUNITY_FILES: ClassVar[list[str]] = [
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
    ]

    COMMUNITY_DOCS: ClassVar[list[str]] = [
        "docs/code_of_conduct.md",
        "docs/contributing.md",
        "docs/license.md",
    ]

    def test_public_has_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Public projects should have all community files."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        for f in self.COMMUNITY_FILES:
            assert (project / f).exists(), f"{f} should exist for public projects"
        for f in self.COMMUNITY_DOCS:
            assert (project / f).exists(), f"{f} should exist for public projects"

    def test_internal_no_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have community files."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        for f in self.COMMUNITY_FILES:
            assert not (project / f).exists(), f"{f} should NOT exist for internal projects"
        for f in self.COMMUNITY_DOCS:
            assert not (project / f).exists(), f"{f} should NOT exist for internal projects"

    def test_internal_no_funding_yml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have FUNDING.yml."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        assert not (project / ".github" / "FUNDING.yml").exists()

    def test_public_has_funding_yml(self, copier_defaults: dict, project_factory) -> None:
        """Public projects should have FUNDING.yml."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        assert (project / ".github" / "FUNDING.yml").exists()

    # -- pyproject.toml license metadata --

    def test_internal_no_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have license metadata in pyproject.toml."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "license = " not in content
        assert "license-files" not in content

    def test_public_has_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Public projects should have license metadata in pyproject.toml."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert 'license = "MIT"' in content
        assert "license-files" in content

    def test_internal_no_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have Funding URL in pyproject.toml."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "Funding" not in content
        assert "sponsors" not in content

    def test_public_has_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Public projects should have Funding URL in pyproject.toml."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "Funding" in content

    # -- mkdocs.yml nav --

    def test_internal_mkdocs_no_community_nav(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects mkdocs.yml should not have community pages in nav."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        assert "License:" not in content
        assert "Contributing:" not in content
        assert "Code of Conduct:" not in content
        assert "copyright:" not in content.lower().split("nav")[0]  # no copyright line

    def test_public_mkdocs_has_community_nav(self, copier_defaults: dict, project_factory) -> None:
        """Public projects mkdocs.yml should have community pages in nav."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        assert "License: license.md" in content
        assert "Contributing: contributing.md" in content
        assert "Code of Conduct: code_of_conduct.md" in content

    def test_internal_mkdocs_no_copyright(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects mkdocs.yml should not have copyright line."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        assert "copyright:" not in content

    def test_public_mkdocs_has_copyright(self, copier_defaults: dict, project_factory) -> None:
        """Public projects mkdocs.yml should have copyright line."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        assert "copyright:" in content

    # -- Core files still present for internal --

    def test_internal_still_has_core_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should still have core project files."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        assert (project / "pyproject.toml").exists()
        assert (project / "README.md").exists()
        assert (project / "CHANGELOG.md").exists()
        assert (project / "prek.toml").exists()
        assert (project / ".editorconfig").exists()
        assert (project / "mkdocs.yml").exists()
        assert (project / "src").is_dir()
        assert (project / "tests").is_dir()

    # -- mkdocs.yml is valid YAML for both --

    def test_internal_mkdocs_valid_yaml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects mkdocs.yml should be valid YAML."""
        import yaml

        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        data = yaml.compose(content)
        assert data is not None

    def test_internal_pyproject_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects pyproject.toml should be valid TOML."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "project" in data

    # -- Lychee config --

    def test_internal_lychee_accepts_401(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should accept 401 for auth-gated URLs."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        content = (project / ".lychee.toml").read_text()
        assert "401" in content

    def test_public_lychee_no_401(self, copier_defaults: dict, project_factory) -> None:
        """Public projects .lychee.toml should not accept 401."""
        answers = {**copier_defaults, "project_visibility": "public"}
        project = project_factory(answers)

        content = (project / ".lychee.toml").read_text()
        assert "401" not in content

    def test_internal_lychee_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should be valid TOML."""
        answers = {**copier_defaults, "project_visibility": "internal"}
        project = project_factory(answers)

        with (project / ".lychee.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "accept" in data

    # -- Self-hosted repository URLs --

    def test_selfhosted_pyproject_urls(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should use repository_host for URLs, no Pages pattern."""
        answers = {
            **copier_defaults,
            "project_visibility": "internal",
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
        }
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "gitlab.company.com" in content
        # URLs should use self-hosted host, not gitlab.com directly
        assert "://gitlab.com/" not in content
        # No Pages URL pattern for self-hosted
        assert ".gitlab.io" not in content

    def test_selfhosted_mkdocs_urls(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should use repository_host in mkdocs.yml."""
        answers = {
            **copier_defaults,
            "project_visibility": "internal",
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
        }
        project = project_factory(answers)

        content = (project / "mkdocs.yml").read_text()
        assert "gitlab.company.com" in content
        # No Pages URL pattern for self-hosted
        assert ".gitlab.io" not in content

    def test_standard_host_uses_pages_urls(self, copier_defaults: dict, project_factory) -> None:
        """Standard github.com/gitlab.com should use Pages URL pattern."""
        project = project_factory(copier_defaults)

        content = (project / "pyproject.toml").read_text()
        assert ".github.io" in content


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

    def test_uv_sync_succeeds(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should successfully run uv sync."""
        project = generate_project(tmp_path, copier_defaults)
        self._init_git_repo(project)

        # Run uv sync
        result = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True)
        assert result.returncode == 0, f"uv sync failed: {result.stderr}"

    @pytest.mark.slow
    def test_verify_scaffold_passes(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project with dev scripts should pass verify-scaffold checks."""
        answers = {**copier_defaults, "include_template_dev_scripts": True, "publish_to_pypi": True}
        project = generate_project(tmp_path, answers)
        self._init_git_repo(project)

        # Run uv sync to create .venv and uv.lock
        sync_result = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True)
        assert sync_result.returncode == 0, f"uv sync failed: {sync_result.stderr}"

        # Run verify-scaffold.sh
        script = project / "scripts" / "verify-scaffold.sh"
        assert script.exists(), "verify-scaffold.sh not generated"
        result = subprocess.run(
            ["bash", str(script)],
            cwd=project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"verify-scaffold.sh failed:\n{result.stdout}\n{result.stderr}"
