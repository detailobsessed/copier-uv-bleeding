---
id: copier-uv-bleeding-5cu
status: closed
deps: []
links: []
created: 2025-12-31T13:09:58.152582+01:00
type: bug
priority: 2
---
# Fix markdownlint errors in template files

The markdownlint pre-commit hook fails on several template files:

**Files affected:**

- CODE_OF_CONDUCT.md - Line length errors (MD013)
- CONTRIBUTING.md - Line length errors (MD013), missing code block language (MD040)
- .github/ISSUE_TEMPLATE/2-feature.md - Heading increment (MD001), line length (MD013)
- .github/ISSUE_TEMPLATE/4-change.md - Heading increment (MD001), line length (MD013)

**Impact:** New projects fail pre-commit hooks on first commit unless --no-verify is used.

**Fix:** Wrap long lines, add language specifiers to code blocks, fix heading levels.
