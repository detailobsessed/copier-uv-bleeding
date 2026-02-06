---
id: copier-uv-bleeding-0h3
status: closed
deps: []
links: []
created: 2025-12-26T22:14:57.134088+01:00
type: task
priority: 3
---
# Move VSCode config from config/vscode to .vscode directly

Currently VSCode settings are in `config/vscode/` and require running `poe vscode` to copy to `.vscode/`. This is an extra step users might forget.

Consider:

- Put `.vscode/` directly in the template
- Or make it a copier question whether to include VSCode config
- Remove the `poe vscode` task if moving directly
