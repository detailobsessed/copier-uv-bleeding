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

Generated projects ship two tasks:

```bash
poe update-template   # copier update --trust . --skip-answered --defaults --conflict inline
poe upgrade           # uv sync --upgrade && uv run prek update
```

`update-template` is copier and nothing else: answered questions are kept, new questions take their defaults, and conflicts are marked inline. Review the result, then run `upgrade` to bring dependencies and hook versions up to date. `prek.toml` keeps `prek update` off pre-release tags and lychee's `nightly`, so running it by hand is safe too.

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
requires = ["uv_build>=0.13.4,<0.14"]
>>>>>>> after updating
```

The top block is yours, the middle one is what the template had before, and the bottom one is what it has now. Keep what you want, delete the markers, and commit. `git grep -l '^<<<<<<<'` lists the files that need it, and the `check-merge-conflict` hook refuses to commit while any marker is left.

Fields rendered from `.copier-answers.yml` (the `[project.urls]`, `[project.scripts]` and repository paths) are recomputed on every update. If you changed one by hand, change the matching answer in `.copier-answers.yml` instead, or the update moves it back.

Since we use Git, run `git status` and `git diff` after `poe update-template` and review the changes before committing. Use `git checkout -- FILE` to drop unwanted changes, or `git add -p` for partial commits.

### Expected once: the Python 3.15 update

This one update deletes lines right next to ones most projects edited, so expect a few conflicts. Each one is resolved the same way: keep your lines and drop the template's old ones.

- **The old `# template-preserve:*` comments** around `dependencies`, your own poe tasks and your own local hooks. Keep your lines and delete the comments. If you added poe tasks, the template's new `upgrade` task lands in the same conflict: keep it alongside yours.
- **`requires-python` next to `version`.** `requires-python` moves above `readme`. The new line merges in on its own, but deleting the old one right above `version` conflicts in every project that has released:

```text
<<<<<<< before updating
requires-python = ">=3.14"
version = "0.18.0"
||||||| last update
requires-python = ">=3.14"
version = "0.0.0"
=======
version = "0.0.0"
>>>>>>> after updating
```

Keep your `version` line and delete the old `requires-python`. Keeping the top block whole leaves two `requires-python` keys, which uv rejects as invalid TOML. After this, `readme` sits between the two lines, and later Python bumps merge without a conflict.

### Updating from 0.42.1 and earlier: once with the old extension

Releases up to 0.42.1 loaded a Jinja extension from `copier-template-extensions`; later ones need only a stock copier. An update renders your project's old template version too, so leaving 0.42.1 or earlier still needs the extension, one last time. With a stock copier the update aborts before writing anything, with `No module named 'copier_template_extensions'`. Run that one update through uvx:

```bash
uvx --with copier-template-extensions copier update --trust --skip-answered --defaults --conflict inline
```

Every later update works with `poe update-template` and any copier, so a `copier` tool installed `--with copier-template-extensions` can be reinstalled plain afterwards.

The author questions no longer default to your git config. That only matters for new projects, since existing ones keep their answers; set defaults once in copier's `settings.yml` instead, as the README describes.

### Updating from 0.41.x: run copier by hand once

Projects from 0.41.14 and earlier run `poe update-template` with `--conflict rej`. In that mode copier moves every hunk it cannot apply cleanly to a `.rej` file, including your unrelated edits next to it, and the file keeps the template's version. Against the Python 3.15 release that takes your released version, dependencies and `[tool.uv]` settings out of `pyproject.toml` and into `pyproject.toml.rej`. Nothing is lost, and the `no-copier-rej-files` hook blocks the commit, but applying `.rej` hunks by hand is tedious. Run the inline update directly instead, through uvx with the old extension as above:

```bash
uvx --with copier-template-extensions copier update --trust --skip-answered --defaults --conflict inline
```

That update brings in the new `poe update-template`, so later updates need nothing special. If you already ran the old task, `git checkout -- .` and `git clean -f '*.rej'` put the project back to where it was.

### Updating from before 0.41.4

The template carries no migrations, so an update across older releases leaves a few things to do by hand. Each one shows up in `git status`:

- **`open_source` (0.41.0)** replaced `project_visibility`, `project_audience` and `use_community_health_files`. The update takes its default, `true` on GitHub and `false` elsewhere, so an internal GitHub project gains a LICENSE and community-health files, and a public GitLab one loses them. Discard those changes and re-run with the right answer: `uvx --with copier-template-extensions copier update --trust --skip-answered --defaults --conflict inline -d open_source=false`.
- **`scripts/prek-autoupdate.sh` (0.41.4)** is no longer used. Delete it.

## What happened in 0.41.0 to 0.41.14

Those releases did not use copier's merge for `pyproject.toml` and `prek.toml`. A task regenerated both files from the template on every update and kept only regions wrapped in `# template-preserve:<name>:start` / `:end` comments, plus `project.version` and `tag_format`. Every other customisation was silently lost: extra ruff ignores, pytest markers, poe task changes, hook revs, `[tool.uv]` settings, optional dependencies (DOT-620, DOT-630).

The task is gone, and both files merge like every other file. The template dropped the `# template-preserve:*` comments with the Python 3.15 release, which is where the one-time conflicts above come from.

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
