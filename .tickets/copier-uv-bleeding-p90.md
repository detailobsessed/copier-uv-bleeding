---
id: copier-uv-bleeding-p90
status: open
deps: []
links: []
created: 2026-02-06T01:50:41.942143+01:00
type: task
priority: 2
---
# Add CI linting hooks to template pre-commit config

Add pre-commit hooks that lint GitHub Actions workflows (actionlint, already present for GitHub) and GitLab CI files for GitLab projects. For GitLab, consider adding a gitlab-ci-lint hook or similar tool to .pre-commit-config.yaml.jinja, gated behind repository_provider == gitlab.com.
