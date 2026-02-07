---
id: cub-tvf1
status: open
deps: []
links: []
created: 2026-02-07T11:28:24Z
type: bug
priority: 2
assignee: Ismar Iljazovic
---
# Exclude copier-update.yml when use_ci is false

## Notes

**2026-02-07T11:28:34Z**

copier-update.yml is a GitHub Actions workflow but isn't excluded when use_ci is false. Add to_exclude: {% if not use_ci %}.github/workflows/copier-update.yml{% endif %}
