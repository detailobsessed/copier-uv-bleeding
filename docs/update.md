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

## Known risk: silent overwrites in `pyproject.toml` and `prek.toml`

`pyproject.toml` and `prek.toml` are deliberately left out of `_skip_if_exists`, so template
improvements (poe tasks, ruff config, hook version bumps) keep flowing into your project via
`copier update`. But that update is **not** a true 3-way merge — it replays the diff between
the old and new template renders as a patch onto your file, using fuzzy context matching. Both
files also carry large, free-form sections you're expected to hand-edit after generation:
`dependencies`, `[project.scripts]`, `[dependency-groups]`, `[[tool.uv.index]]`, and hook
`exclude`/`args` tuning.

When a template release restructures a lot of one of these files at once, the patch can find
*some* plausible anchor nearby and silently overwrite your hand-edited section — **without**
producing a `.rej` file. Seeing no `.rej` files is not proof that nothing was lost.

**Mitigation:** after every `poe update-template` (or bare `copier update`), always run
`git diff pyproject.toml prek.toml` by hand and check that your dependencies, entry points,
dependency-groups, and hook tuning are still there — regardless of whether any `.rej` files
appeared.

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
