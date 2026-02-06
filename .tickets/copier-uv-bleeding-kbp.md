---
id: copier-uv-bleeding-kbp
status: closed
deps: []
links: []
created: 2025-12-26T22:14:53.285959+01:00
type: feature
priority: 2
---
# Add .env.example to template

Many Python projects need environment variables (API keys, database URLs, etc.). The template should include:

- `.env.example` with placeholder comments
- `.env` in `.gitignore` (already present)
- Optional: python-dotenv in dependencies
