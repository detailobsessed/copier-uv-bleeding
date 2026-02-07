---
id: cub-fypd
status: closed
deps: []
links: []
created: 2026-02-07T11:28:18Z
type: bug
priority: 2
assignee: Ismar Iljazovic
---
# Fix stale .vscode/settings.json.jinja paths

## Notes

**2026-02-07T11:28:33Z**

project/.vscode/settings.json.jinja references config/ruff.toml, config/pytest.ini, config/mypy.ini — all consolidated into pyproject.toml. Fix paths or remove stale entries.
