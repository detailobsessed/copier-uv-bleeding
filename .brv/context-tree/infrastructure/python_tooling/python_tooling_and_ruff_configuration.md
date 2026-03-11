---
title: Python Tooling and Ruff Configuration
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-11T23:24:12.011Z'
updatedAt: '2026-03-11T23:24:12.011Z'
---
## Raw Concept

**Task:**
Configure Python project environment (uv, ruff, poe)

**Files:**

- project/pyproject.toml.jinja

**Timestamp:** 2026-03-12

## Narrative

### Structure

Environment is managed via uv with dependency groups (ci, dev, local, docs). Ruff is configured for strict linting with specific overrides for tests.

### Highlights

Target Python 3.14, preview ruff features enabled, comprehensive linting including security (bandit), performance (perflint), and modern idioms (pyupgrade).

### Examples

Poe tasks: `uv run poe lint`, `uv run poe test`, `uv run poe check-template`.
