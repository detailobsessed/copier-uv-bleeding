"""Comprehensive tests for copier template generation."""

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
        "use_ci": True,
        "use_semantic_release": True,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
        "use_polar": False,
    }


def generate_project(
    tmp_path: Path,
    answers: dict,
    project_type: str = "package",
) -> Path:
    """Generate a project using copier."""
    answers = {**answers, "project_type": project_type}

    cmd = [
        "copier",
        "copy",
        "--trust",
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


class TestProjectTypes:
    """Test different project types generate correctly."""

    def test_package_type_has_cli(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Package type should have CLI entry point."""
        project = generate_project(tmp_path, copier_defaults, "package")

        pyproject = project / "pyproject.toml"
        assert pyproject.exists()

        content = pyproject.read_text()
        assert "[project.scripts]" in content
        assert "test-project" in content  # CLI name from slugified project_name

    def test_lib_type_no_cli(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Library type should not have CLI entry point."""
        project = generate_project(tmp_path, copier_defaults, "lib")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[project.scripts]" not in content

    def test_app_type_has_main(self, tmp_path: Path, copier_defaults: dict) -> None:
        """App type should have main.py."""
        project = generate_project(tmp_path, copier_defaults, "app")

        main_py = project / "main.py"
        assert main_py.exists()


class TestCoreFiles:
    """Test core files are generated correctly."""

    def test_pyproject_toml_exists(self, tmp_path: Path, copier_defaults: dict) -> None:
        """pyproject.toml should exist."""
        project = generate_project(tmp_path, copier_defaults)
        assert (project / "pyproject.toml").exists()

    def test_precommit_config_exists(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Pre-commit config should exist."""
        project = generate_project(tmp_path, copier_defaults)
        assert (project / ".pre-commit-config.yaml").exists()

    def test_ruff_config_in_pyproject(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Ruff config should be in pyproject.toml."""
        project = generate_project(tmp_path, copier_defaults)
        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.ruff]" in content
        assert "[tool.ruff.lint]" in content

    def test_src_directory_exists(self, tmp_path: Path, copier_defaults: dict) -> None:
        """src directory should exist."""
        project = generate_project(tmp_path, copier_defaults)
        assert (project / "src").is_dir()

    def test_tests_directory_exists(self, tmp_path: Path, copier_defaults: dict) -> None:
        """tests directory should exist."""
        project = generate_project(tmp_path, copier_defaults)
        assert (project / "tests").is_dir()


class TestCIConfiguration:
    """Test CI configuration options."""

    def test_ci_enabled_creates_workflow(self, tmp_path: Path, copier_defaults: dict) -> None:
        """CI enabled should create workflow file."""
        answers = {**copier_defaults, "use_ci": True}
        project = generate_project(tmp_path, answers)
        assert (project / ".github" / "workflows" / "ci.yml").exists()

    def test_ci_disabled_no_workflow(self, tmp_path: Path, copier_defaults: dict) -> None:
        """CI disabled should not create workflow file."""
        answers = {**copier_defaults, "use_ci": False}
        project = generate_project(tmp_path, answers)
        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_semantic_release_creates_workflow(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Semantic release enabled should create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = generate_project(tmp_path, answers)
        assert (project / ".github" / "workflows" / "release.yml").exists()

    def test_semantic_release_disabled_no_workflow(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Semantic release disabled should not create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": False}
        project = generate_project(tmp_path, answers)
        assert not (project / ".github" / "workflows" / "release.yml").exists()


class TestPythonVersion:
    """Test Python version configuration."""

    def test_requires_python_314(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should require Python 3.14+."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'requires-python = ">=3.14"' in content

    def test_ruff_target_py314(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Ruff should target Python 3.14."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'target-version = "py314"' in content


class TestPreCommitConfig:
    """Test pre-commit configuration."""

    def test_prek_version(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Pre-commit config should have correct prek version."""
        project = generate_project(tmp_path, copier_defaults)

        config = project / ".pre-commit-config.yaml"
        content = config.read_text()
        assert 'minimum_prek_version: "0.3.1"' in content

    def test_has_gitleaks(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Pre-commit config should have gitleaks."""
        project = generate_project(tmp_path, copier_defaults)

        config = project / ".pre-commit-config.yaml"
        content = config.read_text()
        assert "gitleaks" in content

    def test_no_pyupgrade(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Pre-commit config should not have pyupgrade (replaced by ruff UP)."""
        project = generate_project(tmp_path, copier_defaults)

        config = project / ".pre-commit-config.yaml"
        content = config.read_text()
        assert "pyupgrade" not in content


class TestDependencies:
    """Test dependency configuration."""

    def test_no_yore_dependency(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should not have yore dependency."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "yore" not in content

    def test_no_tomli_dependency(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should not have tomli dependency."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tomli" not in content

    def test_prek_version_updated(self, tmp_path: Path, copier_defaults: dict) -> None:
        """prek dependency should be >= 0.3.1."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"prek>=0.3.1"' in content


class TestCIWorkflows:
    """Test CI workflow configuration (from smoke_test.sh assertions)."""

    def test_ci_has_setup_uv(self, tmp_path: Path, copier_defaults: dict) -> None:
        """CI workflow should use setup-uv action."""
        answers = {**copier_defaults, "use_ci": True}
        project = generate_project(tmp_path, answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        content = ci_yml.read_text()
        assert "astral-sh/setup-uv" in content

    def test_ci_poe_tasks_exist_in_pyproject(self, tmp_path: Path, copier_defaults: dict) -> None:
        """All poe tasks referenced in CI workflow should exist in pyproject.toml."""
        import re

        answers = {**copier_defaults, "use_ci": True}
        project = generate_project(tmp_path, answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        pyproject = project / "pyproject.toml"

        ci_content = ci_yml.read_text()
        pyproject_content = pyproject.read_text()

        # Find all poe task references in CI (e.g., "uv run poe check", "uv run poe test")
        poe_tasks = re.findall(r"uv run poe (\w+)", ci_content)

        # Verify each task exists in pyproject.toml
        for task in poe_tasks:
            assert "[tool.poe.tasks]" in pyproject_content, "pyproject.toml should have poe tasks"
            # Check task is defined (either as string or table)
            assert f"{task} = " in pyproject_content or f"{task} = [" in pyproject_content, (
                f"poe task '{task}' referenced in CI but not defined in pyproject.toml"
            )

    def test_release_has_semantic_release(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Release workflow should use semantic-release."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = generate_project(tmp_path, answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "semantic-release" in content

    def test_release_has_uv_publish(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Release workflow should use uv publish."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = generate_project(tmp_path, answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "uv publish" in content

    def test_pyproject_has_build_system(self, tmp_path: Path, copier_defaults: dict) -> None:
        """pyproject.toml should have build-system section."""
        project = generate_project(tmp_path, copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[build-system]" in content


class TestTyperOption:
    """Test typer CLI option."""

    def test_typer_enabled_has_typer_dependency(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Typer enabled should add typer dependency."""
        answers = {**copier_defaults, "use_typer": True}
        project = generate_project(tmp_path, answers, "package")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"typer>=' in content

    def test_typer_disabled_no_typer_dependency(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Typer disabled should not add typer dependency."""
        answers = {**copier_defaults, "use_typer": False}
        project = generate_project(tmp_path, answers, "package")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "typer" not in content

    def test_typer_enabled_uses_typer_in_cli(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Typer enabled should use typer in cli.py."""
        answers = {**copier_defaults, "use_typer": True}
        project = generate_project(tmp_path, answers, "package")

        cli_py = project / "src" / "test_project" / "_internal" / "cli.py"
        content = cli_py.read_text()
        assert "import typer" in content
        assert "app = typer.Typer" in content


class TestIntegration:
    """Integration tests that run uv sync and checks on generated project."""

    def test_uv_sync_succeeds(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should successfully run uv sync."""
        project = generate_project(tmp_path, copier_defaults)

        # Initialize git (required for some tools)
        subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: Initial commit"],
            cwd=project,
            check=True,
            capture_output=True,
            env={
                **subprocess.os.environ,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@test.com",
            },
        )

        # Run uv sync
        result = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True)
        assert result.returncode == 0, f"uv sync failed: {result.stderr}"
