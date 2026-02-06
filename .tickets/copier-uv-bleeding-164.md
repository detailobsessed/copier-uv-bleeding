---
id: copier-uv-bleeding-164
status: closed
deps: []
links: []
created: 2025-12-26T22:14:46.093946+01:00
type: task
priority: 1
---
# Remove or make CLI boilerplate optional

The template includes `_internal/cli.py` and `_internal/debug.py` with argparse boilerplate that:

1. Is a stub that just prints args - not actually useful
2. Forces users to either use it or replace it entirely
3. Not all Python projects need a CLI

Options:

- Remove CLI boilerplate entirely (users can add their own)
- Make it conditional based on project type question
- If keeping, use a modern CLI framework like typer/click instead of argparse
