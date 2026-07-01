"""Migration for the 0.41.0 release: derive `open_source` from the legacy
`project_visibility` / `project_audience` answers.

0.41.0 replaced `project_audience`, `project_visibility` and
`use_community_health_files` with a single `open_source` question. Without
this migration, `copier update --defaults` resolves `open_source` from its
own schema default (`repository_provider == 'github.com'`) instead of the
project's real history — silently flipping visibility for any project whose
history disagrees with that default (e.g. an internal project hosted on
GitHub, or a public project hosted on GitLab). See docs/update.md.

Runs as a `_migrations` "before" step (see copier.yml), so the later
`open_source` question sees a previous answer instead of falling back to its
default. Edits `.copier-answers.yml` with a regex rather than a YAML
library: this script runs via a bare `python3` subprocess in the
destination project's environment, where PyYAML/ruamel are not guaranteed
to be importable (they live in *copier's own* environment, not necessarily
the destination's).
"""

from __future__ import annotations

import re
from pathlib import Path

ANSWERS_FILE = Path(".copier-answers.yml")


def _extract(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(\S+)\s*$", text, re.MULTILINE)
    return match.group(1).strip("'\"") if match else None


def main() -> None:
    if not ANSWERS_FILE.is_file():
        return
    text = ANSWERS_FILE.read_text(encoding="utf-8")
    if re.search(r"^open_source:", text, re.MULTILINE):
        return  # already answered — nothing to derive

    visibility = _extract(text, "project_visibility")
    audience = _extract(text, "project_audience")
    if visibility is not None:
        open_source = visibility == "public"
    elif audience is not None:
        open_source = audience == "public-oss"
    else:
        return  # no legacy answer to derive from; let the question use its own default

    if not text.endswith("\n"):
        text += "\n"
    ANSWERS_FILE.write_text(f"{text}open_source: {str(open_source).lower()}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
