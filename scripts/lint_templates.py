#!/usr/bin/env python3
"""Lint Jinja templates by rendering with edge-case data and validating output.

Catches bugs like:
- Quotes in user input breaking TOML/YAML syntax
- Jinja whitespace control breaking indentation
- Missing/undefined template variables
- Invalid structured file output

Usage:
    python scripts/lint_templates.py [--verbose]

Exit codes:
    0 — all templates valid
    1 — validation errors found
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
import unicodedata
from datetime import date
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "project"

# ---------------------------------------------------------------------------
# Custom Jinja filters/globals (mirrors extensions.py)
# ---------------------------------------------------------------------------


def slugify(value: str, separator: str = "-") -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-_\s]+", separator, value).strip("-_")


# ---------------------------------------------------------------------------
# Context variants — each is a plausible set of copier answers.
# We intentionally include edge-case values (quotes, special chars).
# ---------------------------------------------------------------------------

_COMMON = {
    "current_year": date.today().year,
    "giscus_repo_id": "PLACEHOLDER_REPO_ID",
    "giscus_discussion_category_id": "PLACEHOLDER_CATEGORY_ID",
}


def _build_context(overrides: dict) -> dict:
    """Build a full template context from overrides."""
    base = {
        "project_name": "My Test Project",
        "project_description": "A test project",
        "project_type": "package",
        "author_fullname": "Test Author",
        "author_email": "test@example.com",
        "author_username": "testuser",
        "repository_provider": "github.com",
        "repository_host": "github.com",
        "repository_namespace": "testuser",
        "repository_name": "my-test-project",
        "copyright_holder": "Test Author",
        "copyright_holder_email": "test@example.com",
        "copyright_date": str(date.today().year),
        "copyright_license": "MIT",
        "python_package_distribution_name": "my-test-project",
        "python_package_import_name": "my_test_project",
        "python_package_command_line_name": "my-test-project",
        "use_typer": True,
        "use_ci": True,
        "use_semantic_release": True,
        "publish_to_pypi": True,
        "use_blacksmith_runners": False,
        "project_visibility": "public",
        "use_polar": False,
        "include_template_dev_scripts": False,
        **_COMMON,
    }
    base.update(overrides)
    # Auto-derive repository_host from repository_provider (mirrors copier.yml default)
    if "repository_provider" in overrides and "repository_host" not in overrides:
        base["repository_host"] = overrides["repository_provider"]
    # Derive slug-based fields if project_name changed
    if "project_name" in overrides and "repository_name" not in overrides:
        base["repository_name"] = slugify(overrides["project_name"])
        base["python_package_distribution_name"] = slugify(overrides["project_name"])
        base["python_package_import_name"] = slugify(overrides["project_name"], "_")
        base["python_package_command_line_name"] = slugify(overrides["project_name"])
    return base


CONTEXT_VARIANTS: dict[str, dict] = {
    "github-quotes": _build_context({
        "project_description": 'Helps you "close the loop" on reviews',
        "author_fullname": "Timothée O'Brien",
    }),
    "backslash-edge": _build_context({
        "project_description": 'My "path" is C:\\temp\\',
    }),
    "gitlab-ci": _build_context({
        "repository_provider": "gitlab.com",
        "repository_host": "gitlab.com",
        "use_blacksmith_runners": False,
    }),
    "github-no-ci": _build_context({
        "use_ci": False,
        "use_semantic_release": False,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    "gitlab-no-ci": _build_context({
        "repository_provider": "gitlab.com",
        "repository_host": "gitlab.com",
        "use_ci": False,
        "use_semantic_release": False,
        "publish_to_pypi": False,
        "use_blacksmith_runners": False,
    }),
    "ci-no-pypi": _build_context({
        "use_ci": True,
        "use_semantic_release": True,
        "publish_to_pypi": False,
    }),
    "app-type": _build_context({
        "project_type": "app",
    }),
    "lib-type": _build_context({
        "project_type": "lib",
    }),
    "internal": _build_context({
        "project_visibility": "internal",
        "publish_to_pypi": False,
        "use_polar": False,
    }),
    "internal-selfhosted-gitlab": _build_context({
        "project_visibility": "internal",
        "repository_provider": "gitlab.com",
        "repository_host": "gitlab.company.com",
        "publish_to_pypi": False,
        "use_polar": False,
        "use_blacksmith_runners": False,
    }),
    "internal-selfhosted-github": _build_context({
        "project_visibility": "internal",
        "repository_provider": "github.com",
        "repository_host": "github.company.com",
        "publish_to_pypi": False,
        "use_polar": False,
        "use_blacksmith_runners": False,
    }),
}

# ---------------------------------------------------------------------------
# Validators by file extension
# ---------------------------------------------------------------------------


def validate_toml(content: str, _path: str) -> str | None:
    """Return error message if content is not valid TOML, else None."""
    try:
        tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        return f"Invalid TOML: {exc}"
    return None


def validate_yaml(content: str, _path: str) -> str | None:
    """Return error message if content is not valid YAML, else None.

    Uses yaml.compose() to validate structure without resolving tags like
    !!python/name: used by mkdocs-material.
    """
    try:
        yaml.compose(content)
    except yaml.YAMLError as exc:
        return f"Invalid YAML: {exc}"
    return None


def validate_markdown(content: str, _path: str) -> str | None:
    """Return error message if rendered Markdown has structural issues, else None.

    Checks issues caused by Jinja whitespace control (MD022).
    """
    issues = []
    lines = content.splitlines()
    in_code_block = False
    for i, line in enumerate(lines):
        # Track fenced code blocks (including inside blockquotes)
        stripped = re.sub(r"^(?:>\s*)+", "", line)
        if re.match(r"^```", stripped):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # MD022: Headings must be surrounded by blank lines
        if re.match(r"^#{1,6}\s", line) and i > 0 and lines[i - 1].strip():
            issues.append(f"line {i + 1}: heading without preceding blank line (MD022)")
    if issues:
        return "; ".join(issues)
    return None


VALIDATORS = {
    ".toml": validate_toml,
    ".yml": validate_yaml,
    ".yaml": validate_yaml,
    ".md": validate_markdown,
}

# ---------------------------------------------------------------------------
# Template discovery and rendering
# ---------------------------------------------------------------------------


def get_output_extension(template_path: Path) -> str:
    """Get the output file extension (strip .jinja suffix)."""
    stem = template_path.name
    stem = stem.removesuffix(".jinja")
    # Return the final extension
    if "." in stem:
        return "." + stem.rsplit(".", 1)[1]
    return ""


def has_jinja_in_filename(path: Path) -> bool:
    """Check if the filename itself contains Jinja expressions."""
    name = path.name
    return "{{" in name or "{%" in name


def collect_templates() -> list[Path]:
    """Collect all .jinja template files, skipping those with Jinja in filenames."""
    templates = []
    for path in sorted(TEMPLATE_DIR.rglob("*.jinja")):
        # Skip files whose filename contains Jinja expressions
        if has_jinja_in_filename(path):
            continue
        # Skip files in directories with Jinja expressions
        if any("{{" in part or "{%" in part for part in path.parts):
            continue
        templates.append(path)
    return templates


def render_template(env: Environment, template_path: Path, context: dict) -> str:
    """Render a single template with the given context."""
    rel_path = template_path.relative_to(TEMPLATE_DIR)
    template = env.get_template(str(rel_path))
    return template.render(context)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def lint_templates(verbose: bool = False) -> int:
    """Lint all templates. Returns exit code (0=ok, 1=errors)."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,  # noqa: S701
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["slugify"] = slugify

    templates = collect_templates()
    errors: list[str] = []
    total_checks = 0

    for template_path in templates:
        rel = template_path.relative_to(TEMPLATE_DIR)
        ext = get_output_extension(template_path)
        validator = VALIDATORS.get(ext)

        for variant_name, context in CONTEXT_VARIANTS.items():
            # Skip GitHub-only files for GitLab variants and vice versa
            rel_str = str(rel)
            is_github_file = rel_str.startswith(".github")
            is_gitlab_file = "gitlab-ci" in rel_str
            provider = context.get("repository_provider", "github.com")

            if is_github_file and provider != "github.com":
                continue
            if is_gitlab_file and provider != "gitlab.com":
                continue
            # Skip CI files when CI is disabled
            if not context.get("use_ci") and any(x in rel_str for x in ["ci.yml", "release.yml", "copier-update.yml", "gitlab-ci"]):
                continue
            # Skip community/open-source files for internal projects
            if context.get("project_visibility") == "internal" and any(
                x in rel_str
                for x in [
                    "CODE_OF_CONDUCT",
                    "CONTRIBUTING",
                    "SECURITY",
                    "LICENSE",
                    "license.md",
                    "contributing.md",
                    "code_of_conduct.md",
                    "FUNDING",
                ]
            ):
                continue

            total_checks += 1
            label = f"{rel} [{variant_name}]"

            # 1. Render
            try:
                rendered = render_template(env, template_path, context)
            except UndefinedError as exc:
                errors.append(f"  RENDER FAIL  {label}: {exc}")
                continue
            except Exception as exc:
                errors.append(f"  RENDER FAIL  {label}: {type(exc).__name__}: {exc}")
                continue

            if verbose:
                print(f"  ✓ rendered   {label}")

            # 2. Validate structured output
            if validator:
                error = validator(rendered, label)
                if error:
                    errors.append(f"  INVALID      {label}: {error}")
                elif verbose:
                    print(f"  ✓ validated  {label}")

    # Report
    print(f"\nLinted {len(templates)} templates x {len(CONTEXT_VARIANTS)} variants = {total_checks} checks")

    if errors:
        print(f"\n✗ {len(errors)} error(s) found:\n")
        for err in errors:
            print(err)
        return 1

    print("✓ All templates valid")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true", help="Show each check")
    args = parser.parse_args()
    sys.exit(lint_templates(verbose=args.verbose))
