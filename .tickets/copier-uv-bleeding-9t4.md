---
id: copier-uv-bleeding-9t4
status: closed
deps: []
links: []
created: 2025-12-26T22:14:41.410054+01:00
type: feature
priority: 1
---
# Add project type selection (app/lib/package) like uv init

The template is currently opinionated toward CLI packages, but should support different project types like `uv init` does:

- `--app` - Simple app with `main.py` (no src layout)
- `--lib` - Library with `src/` layout and `py.typed`
- `--package` - Installable package with CLI entry point

Reference: <https://github.com/simonw/uv-init-demos>

Add a copier question to select project type and conditionally include:

- CLI boilerplate only for `package` type
- `main.py` for `app` type
- `src/` layout for `lib` and `package` types
