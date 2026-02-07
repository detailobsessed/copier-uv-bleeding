---
id: cub-3q9c
status: closed
deps: []
links: []
created: 2026-02-07T11:28:13Z
type: bug
priority: 2
assignee: Ismar Iljazovic
---
# Remove dead _skip_if_exists entry for cli.py

## Notes

**2026-02-07T11:28:30Z**

copier.yml line 25: src/{{ python_package_import_name }}/cli.py doesn't match any generated file. Template generates_internal/cli.py. The _internal/ paths are already covered on lines 26-28.
