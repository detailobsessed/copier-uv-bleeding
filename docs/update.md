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

Copier renders the template version your project was last updated to, using your stored answers, and diffs that against your project to find your edits. It then renders the new template version over your files and replays your edits onto it. Where the template changed the same lines you did, it marks the conflict for you to resolve; it never discards your side. Your previous answers are stored in the `.copier-answers.yml` file at the root of the project directory:

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

1. `copier update --trust . --skip-answered --defaults --conflict inline` — pull template changes; previously-answered questions are kept, new questions take their defaults, and conflicts are marked inline
2. `uv sync --upgrade` — upgrade all dependencies
3. `uv run prek update` — update hook versions. The lychee `nightly` tag is excluded declaratively in `prek.toml` under `[update.repos]`, so a bare `prek update` is safe to run by hand too

## Edit any file, including `pyproject.toml` and `prek.toml`

Add dependencies, tables, ignore rules, poe tasks and hooks wherever they belong. Change the template's own values too: a stricter coverage floor, an extra ruff ignore, a different test filter. Copier replays every edit onto the new template version, so an update keeps all of them.

The hook `rev` lines are yours as well. The template ships them empty and never changes those lines, so the revs `prek update` and the `sync-with-uv` hook write survive every update.

## Handling conflicts

When a release changes a line you also changed, or one right next to it, copier keeps both versions and marks the spot in the file:

```text
<<<<<<< before updating
requires = ["uv_build>=0.13,<0.14"]
||||||| last update
requires = ["uv_build>=0.12.1,<0.13"]
=======
requires = ["uv_build>=0.13.2,<0.14"]
>>>>>>> after updating
```

The top block is yours, the middle one is what the template had before, and the bottom one is what it has now. Keep what you want, delete the markers, and commit. `poe update-template` lists the files that need it, and the `check-merge-conflict` hook refuses to commit while any marker is left.

Fields rendered from `.copier-answers.yml` (the `[project.urls]`, `[project.scripts]` and repository paths) are recomputed on every update. If you changed one by hand, change the matching answer in `.copier-answers.yml` instead, or the update moves it back.

Since we use Git, run `git status` and `git diff` after `poe update-template` and review the changes before committing. Use `git checkout -- FILE` to drop unwanted changes, or `git add -p` for partial commits.

## What happened in 0.41.0 to 0.41.14

Those releases did not use copier's merge for `pyproject.toml` and `prek.toml`. A task regenerated both files from the template on every update and kept only regions wrapped in `# template-preserve:<name>:start` / `:end` comments, plus `project.version` and `tag_format`. Every other customisation was silently lost: extra ruff ignores, pytest markers, poe task changes, hook revs, `[tool.uv]` settings, optional dependencies (DOT-620, DOT-630).

The task is gone, and both files merge like every other file. The `# template-preserve:*` comments are still in the template and in your project, but nothing reads them any more. Delete them if you like. The template keeps them because deleting a line right next to one you edited, like `dependencies`, would be a conflict in nearly every project's next update.

If an earlier update lost something, `git log -p pyproject.toml prek.toml` shows what it was. One loss needs care: if an update reset your `tag_format` **and a release ran on the wrong format**, restoring the line is not enough, because semantic-release has no tag it recognizes any more. Tag the last good release commit in the correct format first (`git tag -a v0.9.0 <sha>`), then release normally.

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
