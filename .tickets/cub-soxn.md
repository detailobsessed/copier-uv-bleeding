---
id: cub-soxn
status: closed
deps: []
links: []
created: 2026-02-07T11:28:21Z
type: bug
priority: 3
assignee: Ismar Iljazovic
---
# Add main.py to _skip_if_exists for app type adopt

## Notes

**2026-02-07T11:28:36Z**

main.py for app type is user-owned code per the stated philosophy but isn't in _skip_if_exists. During copier adopt on existing app, creates conflicts on their main entry point.
