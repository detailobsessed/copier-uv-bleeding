---
id: cub-9w9e
status: closed
deps: []
links: []
created: 2026-02-07T11:28:23Z
type: feature
priority: 3
assignee: Ismar Iljazovic
---
# Review LICENSE _skip_if_exists behavior for adopt

## Notes

**2026-02-07T11:28:38Z**

During adopt, LICENSE gets conflict markers if it differs from template-generated version. May be fine since user picks license in prompt. Decide if this should be in _skip_if_exists.
