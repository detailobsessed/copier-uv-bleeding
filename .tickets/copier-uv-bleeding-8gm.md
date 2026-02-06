---
id: copier-uv-bleeding-8gm
status: closed
deps: []
links: []
created: 2025-12-26T22:14:50.298507+01:00
type: task
priority: 2
---
# Make credits.md and gen_credits.py optional

The template includes a 173-line `scripts/gen_credits.py` that auto-generates a credits page listing all dependencies. While nice, it:

- Adds complexity (jinja2, packaging dependencies)
- Most projects won't use this feature
- Adds maintenance burden

Options:

- Make it optional via copier question
- Simplify to a static credits page
- Remove entirely (users can add if needed)
