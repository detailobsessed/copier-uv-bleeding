"""Test that Jinja templates render valid structured output.

Replaces scripts/lint_templates.py with proper pytest parametrization and
hypothesis-based property testing for string edge cases.

Tests two properties:
1. All templates render without errors for each context variant (parametrized)
2. TOML/YAML templates produce valid output for arbitrary string inputs (hypothesis)
"""

from __future__ import annotations

import ast
import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from extensions import slugify

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "project"

# ---------------------------------------------------------------------------
# Template rendering infrastructure
# ---------------------------------------------------------------------------

_ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)
_ENV.filters["slugify"] = slugify


def _build_context(overrides: dict) -> dict:
    """Build a full template context from overrides."""
    base = {
        "project_name": "My Test Project",
        "project_description": "A test project",
        "project_type": "app",
        "author_fullname": "Test Author",
        "author_email": "test@example.com",
        "author_username": "testuser",
        "repository_provider": "github.com",
        "repository_host": "github.com",
        "repository_namespace": "testuser",
        "repository_name": "my-test-project",
        "copyright_license": "MIT",
        "python_package_distribution_name": "my-test-project",
        "python_package_import_name": "my_test_project",
        "python_package_command_line_name": "my-test-project",
        "use_docs": True,
        "use_heavy_hooks": True,
        "use_ci": True,
        "use_semantic_release": True,
        "publish_to_pypi": True,
        "publish_to_mcp_registry": False,
        "use_custom_pypi_index": False,
        "use_blacksmith_runners": False,
        "configure_repo_settings": False,
        "project_audience": "public-oss",
        "project_visibility": "public",
        "use_community_health_files": True,
        "custom_pypi_index_url": "",
        "current_year": datetime.now(UTC).year,
    }
    base.update(overrides)
    if "repository_provider" in overrides and "repository_host" not in overrides:
        base["repository_host"] = overrides["repository_provider"]
    if "project_name" in overrides and "repository_name" not in overrides:
        base["repository_name"] = slugify(overrides["project_name"])
        base["python_package_distribution_name"] = slugify(overrides["project_name"])
        base["python_package_import_name"] = slugify(overrides["project_name"], "_")
        base["python_package_command_line_name"] = slugify(overrides["project_name"])
    return base


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def _validate_toml(content: str) -> str | None:
    try:
        tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        return f"Invalid TOML: {exc}"
    return None


def _validate_yaml(content: str) -> str | None:
    try:
        yaml.compose(content)
    except yaml.YAMLError as exc:
        return f"Invalid YAML: {exc}"
    return None


def _validate_markdown(content: str) -> str | None:
    issues = []
    lines = content.splitlines()
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = re.sub(r"^(?:>\s*)+", "", line)
        if re.match(r"^```", stripped):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r"^#{1,6}\s", line) and i > 0 and lines[i - 1].strip():
            issues.append(f"line {i + 1}: heading without preceding blank line (MD022)")
    if issues:
        return "; ".join(issues)
    return None


def _validate_python(content: str) -> str | None:
    try:
        ast.parse(content)
    except SyntaxError as exc:
        return f"Invalid Python: {exc}"
    return None


def _validate_json(content: str) -> str | None:
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON: {exc}"
    return None


_VALIDATORS = {
    ".toml": _validate_toml,
    ".yml": _validate_yaml,
    ".yaml": _validate_yaml,
    ".json": _validate_json,
    ".md": _validate_markdown,
    ".py": _validate_python,
}


# ---------------------------------------------------------------------------
# Template discovery
# ---------------------------------------------------------------------------


def _get_output_extension(template_path: Path) -> str:
    stem = template_path.name.removesuffix(".jinja")
    if "." in stem:
        return "." + stem.rsplit(".", 1)[1]
    return ""


def _collect_templates() -> list[Path]:
    templates = []
    for path in sorted(TEMPLATE_DIR.rglob("*.jinja")):
        if "{{" in path.name or "{%" in path.name:
            continue
        if any("{{" in part or "{%" in part for part in path.parts):
            continue
        templates.append(path)
    return templates


_COMMUNITY_HEALTH_FILES = (
    "CODE_OF_CONDUCT",
    "CONTRIBUTING",
    "SECURITY",
    "contributing.md",
    "code_of_conduct.md",
    "FUNDING",
    "ISSUE_TEMPLATE",
    "pull_request_template",
)
_LICENSE_FILES = ("LICENSE", "license.md")


def _should_skip(rel_str: str, context: dict) -> bool:
    provider = context.get("repository_provider", "github.com")
    skip_rules = (
        (rel_str.startswith(".github") and provider != "github.com"),
        ("gitlab-ci" in rel_str and provider != "gitlab.com"),
        (not context.get("use_ci") and any(x in rel_str for x in ("ci.yml", "gitlab-ci"))),
        (not context.get("use_semantic_release") and "release.yml" in rel_str),
        (not context.get("publish_to_mcp_registry") and "mcp-registry-publish.yml" in rel_str),
        (not context.get("use_docs") and any(x in rel_str for x in ("docs/", "docs.yml", "zensical.toml"))),
        (not context.get("use_community_health_files", True) and any(x in rel_str for x in _COMMUNITY_HEALTH_FILES)),
        (context.get("project_visibility") == "internal" and any(x in rel_str for x in _LICENSE_FILES)),
    )
    return any(skip_rules)


_TEMPLATES = _collect_templates()

# ---------------------------------------------------------------------------
# Context variants — exhaustive coverage of boolean/enum branches
# ---------------------------------------------------------------------------

CONTEXT_VARIANTS: dict[str, dict] = {
    # GitHub defaults (most common path)
    "github-defaults": _build_context({}),
    # String edge cases
    "github-quotes": _build_context({
        "project_description": 'Helps you "close the loop" on reviews',
        "author_fullname": "Timothée O'Brien",
    }),
    "backslash-edge": _build_context({
        "project_description": 'My "path" is C:\\temp\\',
    }),
    # GitLab
    "gitlab-ci": _build_context({
        "repository_provider": "gitlab.com",
    }),
    "gitlab-no-ci": _build_context({
        "repository_provider": "gitlab.com",
        "use_ci": False,
        "use_semantic_release": False,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    # CI toggling
    "github-no-ci": _build_context({
        "use_ci": False,
        "use_semantic_release": False,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    "ci-no-release": _build_context({
        "use_semantic_release": False,
        "publish_to_pypi": False,
    }),
    "ci-no-pypi": _build_context({
        "use_semantic_release": True,
        "publish_to_pypi": False,
    }),
    "no-docs": _build_context({
        "use_docs": False,
    }),
    # Lightweight hooks — pytest-cov and docs-build dropped from git hooks
    "lightweight-hooks": _build_context({
        "use_heavy_hooks": False,
    }),
    "no-docs-no-ci": _build_context({
        "use_docs": False,
        "use_ci": False,
        "use_semantic_release": False,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    # Blacksmith runners (previously untested)
    "blacksmith-runners": _build_context({
        "use_blacksmith_runners": True,
    }),
    "blacksmith-with-pypi": _build_context({
        "use_blacksmith_runners": True,
        "publish_to_pypi": True,
    }),
    # Project types
    "lib-type": _build_context({"project_type": "lib"}),
    # Community-health toggle (independent of visibility)
    "public-no-community": _build_context({
        "use_community_health_files": False,
    }),
    # Visibility
    "internal": _build_context({
        "project_visibility": "internal",
        "use_community_health_files": False,
        "publish_to_pypi": False,
    }),
    "internal-selfhosted-gitlab": _build_context({
        "project_visibility": "internal",
        "use_community_health_files": False,
        "repository_provider": "gitlab.com",
        "repository_host": "gitlab.company.com",
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    "internal-selfhosted-github": _build_context({
        "project_visibility": "internal",
        "use_community_health_files": False,
        "repository_provider": "github.com",
        "repository_host": "github.company.com",
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    # MCP registry publishing
    "mcp-registry-publish": _build_context({
        "publish_to_mcp_registry": True,
    }),
    # Custom PyPI index (corporate Artifactory/Nexus)
    "custom-pypi-index": _build_context({
        "project_visibility": "internal",
        "use_community_health_files": False,
        "use_custom_pypi_index": True,
        "custom_pypi_index_url": "https://artifactory.company.com/api/pypi/python-virtual/simple",
        "publish_to_pypi": False,
    }),
}


# ---------------------------------------------------------------------------
# Parametrized tests — one run per context variant
# ---------------------------------------------------------------------------


class TestTemplateLint:
    """All templates render without errors and produce valid structured output."""

    @pytest.mark.parametrize(
        ("variant_name", "context"),
        list(CONTEXT_VARIANTS.items()),
        ids=list(CONTEXT_VARIANTS.keys()),
    )
    def test_renders_valid_output(self, variant_name: str, context: dict) -> None:
        errors = []
        for template_path in _TEMPLATES:
            rel = template_path.relative_to(TEMPLATE_DIR)
            rel_str = str(rel)
            if _should_skip(rel_str, context):
                continue

            label = f"{rel} [{variant_name}]"

            try:
                template = _ENV.get_template(str(rel))
                rendered = template.render(context)
            except Exception as exc:
                errors.append(f"RENDER FAIL {label}: {exc}")
                continue

            ext = _get_output_extension(template_path)
            validator = _VALIDATORS.get(ext)
            if validator:
                error = validator(rendered)
                if error:
                    errors.append(f"INVALID {label}: {error}")

        assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# Hypothesis tests — string fuzzing for structured output
# ---------------------------------------------------------------------------

# Characters that commonly break TOML/YAML: quotes, backslashes, colons, etc.
_user_text = st.text(
    min_size=1,
    max_size=80,
    alphabet=st.characters(
        categories=("L", "M", "N", "P", "S", "Z"),
        exclude_characters=("\x00",),
    ),
)


class TestPyprojectGroups:
    """Assertions about dependency groups in rendered pyproject.toml."""

    def _render_pyproject(self, context: dict) -> dict:
        template = _ENV.get_template("pyproject.toml.jinja")
        rendered = template.render(context)
        return tomllib.loads(rendered)

    def test_dev_group_in_default_groups(self) -> None:
        """dev group must be in default-groups so existing projects keep their deps after copier update."""
        data = self._render_pyproject(_build_context({}))
        default_groups = data["tool"]["uv"]["default-groups"]
        assert "dev" in default_groups, f"'dev' missing from default-groups: {default_groups}"

    @pytest.mark.parametrize(
        ("variant_name", "context"),
        list(CONTEXT_VARIANTS.items()),
        ids=list(CONTEXT_VARIANTS.keys()),
    )
    def test_all_default_groups_are_defined(self, variant_name: str, context: dict) -> None:
        """Every group listed in default-groups must exist in [dependency-groups].

        Parametrized over CONTEXT_VARIANTS so each variant gets its own test node;
        the previous `for`-loop form short-circuited on the first failing variant
        and hid downstream failures (DOT-284).
        """
        del variant_name  # variant identity is carried by the pytest parametrize id
        data = self._render_pyproject(context)
        default_groups = data["tool"]["uv"]["default-groups"]
        defined_groups = set(data.get("dependency-groups", {}).keys())
        missing = [g for g in default_groups if g not in defined_groups]
        assert not missing, f"groups in default-groups but not defined: {missing}"


class TestStringFuzzing:
    """TOML and YAML templates produce valid output for arbitrary string inputs."""

    @given(project_description=_user_text, author_fullname=_user_text)
    @settings(max_examples=100)
    def test_toml_survives_special_strings(
        self,
        project_description: str,
        author_fullname: str,
    ) -> None:
        context = _build_context({
            "project_description": project_description,
            "author_fullname": author_fullname,
        })
        for template_path in _TEMPLATES:
            rel = template_path.relative_to(TEMPLATE_DIR)
            if _get_output_extension(template_path) != ".toml":
                continue
            if _should_skip(str(rel), context):
                continue
            rendered = _ENV.get_template(str(rel)).render(context)
            error = _validate_toml(rendered)
            assert error is None, f"{rel}: {error} (description={project_description!r}, author={author_fullname!r})"

    @given(project_description=_user_text, author_fullname=_user_text)
    @settings(max_examples=100)
    def test_yaml_survives_special_strings(
        self,
        project_description: str,
        author_fullname: str,
    ) -> None:
        context = _build_context({
            "project_description": project_description,
            "author_fullname": author_fullname,
        })
        for template_path in _TEMPLATES:
            rel = template_path.relative_to(TEMPLATE_DIR)
            ext = _get_output_extension(template_path)
            if ext not in {".yml", ".yaml"}:
                continue
            if _should_skip(str(rel), context):
                continue
            rendered = _ENV.get_template(str(rel)).render(context)
            error = _validate_yaml(rendered)
            assert error is None, f"{rel}: {error} (description={project_description!r}, author={author_fullname!r})"
