# Updating a project

Copier has an "update" feature.
It means that, once a project is generated,
you can keep updating it with the latest changes
that happen in the template.

It's particularly useful when you manage a lot of projects,
all generated from the same template, and you want to
apply a change to all your projects.

Example: the template updated a dependency version or fixed a CI workflow.
You don't want to apply it manually to your projects.

To update your project, go into its directory,
and run `copier update`. Your repository must be clean
(no modified files) when running this command.

Copier will use the previous answers you gave when
generating the project, to re-generate it in a temporary
directory, compare the two versions, and apply patches
to your documents. When it's not sure, or when there's
a conflict, it will ask you if you want to skip that
change or force it. Your previous answers are stored
in the `.copier-answers.yml` file at the root
of the project directory:

```
📁 my-project
├── 📄 .copier-answers.yml
└── 📄 etc.
```

And the file looks like this:

```yaml
# Changes here will be overwritten by Copier
_commit: 0.1.10
_src_path: gh:detailobsessed/copier-uv-bleeding
author_email: ismar@gmail.com
author_fullname: Ismar Iljazovic
author_username: detailobsessed
copyright_license: ISC License
project_description: Automatic documentation from sources, for MkDocs.
project_name: mkdocstrings
python_package_command_line_name: ""
python_package_distribution_name: mkdocstrings
python_package_import_name: mkdocstrings
repository_name: mkdocstrings
repository_namespace: mkdocstrings
repository_provider: github.com
```

Generated projects ship a `poe update-template` task that handles the full update flow:

```bash
poe update-template
```

This runs:

1. `copier update --trust . --skip-answered --conflict rej` — pull template changes; previously-answered questions are kept, new questions are surfaced interactively, conflicts produce `.rej` files instead of inline conflict markers
2. `uv sync --upgrade` — upgrade all dependencies
3. `bash scripts/prek-autoupdate.sh` — update hook versions (wraps `prek autoupdate` with a lychee `nightly` workaround; see `scripts/prek-autoupdate.sh`)

## Handling conflicts

`copier update` may produce two kinds of artefacts you need to handle before committing:

1. **`.rej` files** — wherever the template's diff couldn't be applied cleanly, Copier writes the rejected hunk to `<file>.rej` alongside the original. The original file keeps your working content; the `.rej` file holds the change the template wanted. Review each `.rej`, apply what's useful by hand, then delete it. A pre-commit hook (`no-copier-rej-files`) refuses to commit while `.rej` files exist.
2. **Re-rendered templated values** — fields rendered from `.copier-answers.yml` (e.g. `[project.urls]`, `[project.scripts]`, repository paths) are recomputed on every update. If you manually edited those without bumping the matching answer, the update will reset them. Fix the answer in `.copier-answers.yml` instead of editing the rendered file.

Since we use Git, run `git status` and `git diff` after `poe update-template` and review the changes before committing. Use `git checkout -- FILE` to drop unwanted changes, or `git add -p` for partial commits.

## How `pyproject.toml` and `prek.toml` update (DOT-599)

Both files mix template-owned config (most of the file — `[tool.ruff]`, `[tool.pytest.ini_options]`,
poe tasks, hook definitions, ...) with content you're expected to grow over time (`dependencies`,
`[project.scripts]`, `[dependency-groups]` contents, `[[tool.uv.index]]`, your own hooks) in one
file, by design.

Copier's default `copier update` is **not** a true 3-way merge — it replays the diff between the
old and new template renders as a patch onto your file, using fuzzy context matching. On a
release that restructures a lot of the file at once, that patch can find *some* plausible anchor
nearby and silently overwrite a hand-edited section, **without** producing a `.rej` file. That
bug is exactly what happened in the incident DOT-599 is named after.

Because of that, both files are listed in `_skip_if_exists`, so Copier's default patcher never
touches them after first generation. Instead, a `_tasks` step runs
`migrations/sync_marked_sections.py` on every `copier update`, which **regenerates the whole file
fresh from the template every time**, except for regions explicitly wrapped in
`# template-preserve:<name>:start` / `# template-preserve:<name>:end` comments in the `.jinja`
source (e.g. around `dependencies`, `[project.scripts]`, `[dependency-groups]`,
`[[tool.uv.index]]`, and a dedicated "extra poe tasks" / "extra local hooks" slot in each file) —
those are copied byte-for-byte from your previous version. Regions are matched **by name**, not
by position, so a release that reorders or inserts a marked region can't splice content into the
wrong slot.

**Only marked regions survive an update — everything else always reflects the template.** If you
add something the template has no marker for (a brand-new `[tool.x]` table, an extra dependency
index before you've ever answered the custom-index question, a hand-written poe task outside the
"extra poe tasks" slot), it will be silently dropped on the next update. This is a real trade-off
versus the file-level "leave anything unrecognized alone" approach this template used briefly
before markers: predictable and documented, but stricter. Two things matter in practice:

- `[[tool.uv.index]]` only gets a marker at all in projects that answered `custom_pypi_index_url`
  at generation time. If you never answered it and later hand-add a `[[tool.uv.index]]` block, it
  will not survive the next update — re-run `copier update` after setting the answer instead.
- For custom poe tasks / local hooks, use the dedicated "extra poe tasks" / "extra local hooks"
  slots, not an arbitrary spot in the file — anything outside those slots follows the same rule.

Existing projects generated before this mechanism shipped have none of these markers yet. Their
first update to a marker-aware template version runs a one-time bootstrap
(`_bootstrap_legacy_markers` in `migrations/sync_marked_sections.py`) that locates the equivalent
pre-marker content for each of the structural regions above and wraps it in place before syncing,
and — for the two "extra" slots — moves any task/hook whose name the template doesn't recognize
into the new slot. It's best-effort text matching, not a TOML parser, so unusual formatting (a
hand-reformatted multi-line `dependencies` array, for example) may not bootstrap cleanly; always
`git diff` after the first update past this change.

This approach is adapted from a small third-party tool called
[Templator](https://github.com/dariusgm/templator) (not a dependency — its idea, reimplemented
here in ~70 lines with no TOML library needed) with two deliberate fixes over its own
implementation: it matches by name instead of position, and it never blanks a region that's never
been snapshotted (Templator's own implementation empties any marked region with no snapshot, even
on first generation — a footgun for a template that seeds real default content inside a marked
region, like this template's CLI entry point).

If you want a new spot users can customize without losing it on update, wrap it in
`# template-preserve:<name>:start` / `:end` in the `.jinja` source — nothing else to register or
maintain. Anything *not* wrapped always reflects the latest template release.

## Never hand-edit `.copier-answers.yml`

Copier reconstructs the "old" version of your project (to compute what changed) from the full
history of answers in `.copier-answers.yml`, including keys for questions the current template
no longer asks. If you delete a deprecated key by hand — for example because a newer template
version renamed or merged that question into a new one — Copier falls back to that old template
version's schema *default* instead of your project's real history when reconstructing that old
render. That produces a wrong baseline for the diff, which can silently delete or revert
unrelated customizations elsewhere in the project. Leave deprecated keys in place; Copier stops
writing them once the corresponding question is gone, but still needs them for one more update
to compute history correctly.
