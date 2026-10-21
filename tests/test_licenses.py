"""Every license copier.yml offers must be a REUSE license under its REUSE name, and render."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
import reuse
import yaml
from jinja2 import Environment

REPO_ROOT = Path(__file__).resolve().parent.parent

with (REPO_ROOT / "copier.yml").open(encoding="utf-8") as file:
    LICENSES = {identifier: name for name, identifier in yaml.safe_load(file)["copyright_license"]["choices"].items()}

with Path(reuse.__file__).parent.joinpath("resources", "licenses.json").open(encoding="utf-8") as file:
    REUSE_LICENSES = {ldata["licenseId"]: ldata["name"] for ldata in json.load(file)["licenses"]}


@pytest.mark.parametrize(("identifier", "name"), LICENSES.items())
def test_license_matches_reuse(identifier: str, name: str) -> None:
    assert identifier in REUSE_LICENSES, f"License {identifier} is not supported by REUSE."
    assert name == REUSE_LICENSES[identifier], f"License {identifier} has a different name in REUSE"


@pytest.mark.parametrize("identifier", LICENSES)
def test_license_renders(identifier: str) -> None:
    # Copier loads jinja2-ansible-filters into every render; the year comes from its `strftime`.
    env = Environment(autoescape=False, extensions=["jinja2_ansible_filters.AnsibleCoreFiltersExtension"])
    template = env.from_string((REPO_ROOT / "project" / "LICENSE.jinja").read_text(encoding="utf-8"))
    rendered = template.render(
        project_name="Test Project",
        project_description="Testing this great template",
        author_fullname="Jane Doe",
        author_username="janedoe",
        author_email="jane@example.com",
        copyright_license=identifier,
    )
    assert rendered.strip(), "License is empty!"
    if "Jane Doe" in rendered:
        assert time.strftime("%Y") in rendered, "Copyright line lacks the current year"
