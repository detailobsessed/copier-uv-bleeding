# Learning Tools

Notable tooling features, tips, and discoveries. Tracked here so knowledge is portable and doesn't rely on AI memory alone.

## prek (pre-commit runner)

**Version**: 0.3.2 (2026-02-06)

### prek.toml (new in 0.3.2)

TOML alternative to `.pre-commit-config.yaml`. Less error-prone, cleaner structure. Convert with `prek util yaml-to-toml`. If both exist, `prek.toml` takes precedence.

### Glob patterns (prek-only)

`files` and `exclude` accept glob patterns instead of regex:

```toml
# Instead of regex:
files = "^(docs/|src/)"

# Use glob (prek-only, not portable to upstream pre-commit):
files = { glob = ["docs/**", "src/**"] }
```

Glob syntax: [globset docs](https://docs.rs/globset/latest/globset/#syntax)

### Priority-based parallel execution (0.2.23+)

Hooks with the same `priority` value run in parallel. Use `priority = 0` for instant builtin hooks, `priority = 1` for everything else.

### `prek util identify`

Shows file identification tags prek uses for filtering. Useful for debugging `types`/`types_or`/`exclude_types` filters:

```bash
prek util identify src/mypackage/main.py
```

### `PREK_QUIET` env var

- `PREK_QUIET=1` — only show failed hooks (equivalent to `-q`)
- `PREK_QUIET=2` — silent mode (equivalent to `-qq`)

Useful in CI workflows for cleaner output.

### JSON Schema

IDE validation for `prek.toml`: `https://prek.j178.dev/docs/prek.schema.json`

Add to VS Code / Windsurf settings:

```json
"evenBetterToml.schema.associations": {
  "**/prek.toml": "https://prek.j178.dev/docs/prek.schema.json"
}
```

### `.prekignore`

Like `.gitignore`, excludes directories from workspace discovery. Run with `--refresh` after changes.

---

## ruff

**Version**: 0.15.x

### Rule selection strategy

Use `select` (explicit list) not `extend-select` for full control. Ruff defaults are only E and F.

### Per-file-ignores for tests

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # Allow assert in tests
```

---

## ty (type checker)

**Version**: 0.0.14+

### `requires-python` matters

ty reads `requires-python` from `pyproject.toml` to determine stdlib availability. If set to `>=3.10`, ty won't resolve `tomllib` (3.11+). Set to `>=3.14` for bleeding edge.

### Configuration

```toml
[tool.ty.environment]
python-version = "3.14"
```

---

## actionlint (GitHub Actions linter)

### Cross-repo reusable workflow limitations

actionlint **cannot** validate permissions of cross-repo reusable workflows. It only checks local YAML syntax. If a reusable workflow requests `id-token: write` but the caller only grants `contents: write`, actionlint won't catch the mismatch. GitHub rejects this at parse time with:

> The nested job 'release' is requesting 'id-token: write', but is only allowed 'id-token: none'

### Script injection detection

actionlint can detect some `${{ }}` expression injection in `run:` steps, but not all cases. Always use the env variable pattern:

```yaml
# Bad — shell injection risk:
run: uv sync --group ${{ inputs.dependency-group }}

# Good — safe:
env:
  DEP_GROUP: ${{ inputs.dependency-group }}
run: uv sync --group "$DEP_GROUP"
```

Safe contexts (not shell): `with:`, `runs-on:`, `if:`

---

## uv

### Trusted publishing caveat

PyPI OIDC trusted publishing does NOT work from reusable GitHub Actions workflows. The `job_workflow_ref` claim points to the reusable workflow's repo, not the caller's. Always run `uv publish` in the calling workflow.

---

## copier

### `_skip_if_exists` vs `_exclude`

- `_skip_if_exists`: Skips overwriting if file exists, but creates if missing. Correct for user-owned files.
- `_exclude`: Permanently prevents file generation. Once excluded, `copier update` can never bring it back. Only use for feature-gated files.

### `_commit` field

Tracks which template tag was used. If tags are deleted, `copier update` fails. Fix by updating `_commit` to a valid tag.
