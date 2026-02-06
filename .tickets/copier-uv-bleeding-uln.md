---
id: copier-uv-bleeding-uln
status: closed
deps: []
links: []
created: 2025-12-26T22:15:01.330544+01:00
type: task
priority: 3
---
# Consider Python-native alternative to commitlint.config.js

The template includes `commitlint.config.js` - a JavaScript file in a Python project. This is used by the commitlint pre-commit hook.

Options:

- Keep as-is (it works, just feels out of place)
- Use conventional-pre-commit instead (already in ismar.ch config)
- Make commitlint optional via copier question
