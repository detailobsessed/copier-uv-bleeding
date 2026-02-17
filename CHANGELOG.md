# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

---

**Note:** This is a fork of [pawamoy/copier-uv](https://github.com/pawamoy/copier-uv).
See the original repository for historical changes before version 2.0.0.

---

<!-- version list -->

## v0.29.0 (2026-02-17)

### Features

- Add custom PyPI index support without default=true
  ([#232](https://github.com/detailobsessed/copier-uv-bleeding/pull/232),
  [`393747a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/393747aa74a493d95130f855df2b8b77827d1dfa))

- Enable auto-merge on repos ([#234](https://github.com/detailobsessed/copier-uv-bleeding/pull/234),
  [`333396f`](https://github.com/detailobsessed/copier-uv-bleeding/commit/333396f594a8edc2984814fffba2ff3b1214b9a2))


## v0.28.5 (2026-02-17)

### Bug Fixes

- Default use_ci to false for internal projects
  ([#231](https://github.com/detailobsessed/copier-uv-bleeding/pull/231),
  [`9d8652e`](https://github.com/detailobsessed/copier-uv-bleeding/commit/9d8652e68fcb02c7d7222b41329acafbd51d0c41))

- Minor template polish — provider-neutral badge text and stale coverage omit
  ([#230](https://github.com/detailobsessed/copier-uv-bleeding/pull/230),
  [`0848731`](https://github.com/detailobsessed/copier-uv-bleeding/commit/084873138c5943df5dec541e12b1e0a09286c38b))


## v0.28.4 (2026-02-15)

### Bug Fixes

- Add -q flag to pytest hooks for quieter output
  ([#227](https://github.com/detailobsessed/copier-uv-bleeding/pull/227),
  [`27c32ab`](https://github.com/detailobsessed/copier-uv-bleeding/commit/27c32ab0ca0bd073597d0e422749ad7a1fc1428f))


## v0.28.3 (2026-02-13)

### Refactoring

- Collapse project_type to 2 choices and add cli_framework
  ([#225](https://github.com/detailobsessed/copier-uv-bleeding/pull/225),
  [`e1ff6d5`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e1ff6d512596d6e8fe89056729c66f224b16da16))


## v0.28.2 (2026-02-13)

### Bug Fixes

- Tty notification and verbose hooks
  ([#224](https://github.com/detailobsessed/copier-uv-bleeding/pull/224),
  [`3c5175a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/3c5175a2935bc16fcebce96f05b630b80af26474))


## v0.28.1 (2026-02-13)

### Documentation

- Refine ruff rules and rewrite CONTRIBUTING
  ([#223](https://github.com/detailobsessed/copier-uv-bleeding/pull/223),
  [`30cced6`](https://github.com/detailobsessed/copier-uv-bleeding/commit/30cced69e565b68b17369e0957ef7a30de596155))


## v0.28.0 (2026-02-13)

### Continuous Integration

- Expand semantic-release patch_tags for aggressive template releases
  ([#222](https://github.com/detailobsessed/copier-uv-bleeding/pull/222),
  [`e291507`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e2915074ded91b0e2f970275cd58e101fc56ffb9))

### Features

- Add ci-pass gate job for branch protection
  ([#219](https://github.com/detailobsessed/copier-uv-bleeding/pull/219),
  [`1bb36ee`](https://github.com/detailobsessed/copier-uv-bleeding/commit/1bb36eec049d80af9e8a190e969c5ef8ea690aea))

### Refactoring

- Convert lint_templates.py to pytest+hypothesis test
  ([#220](https://github.com/detailobsessed/copier-uv-bleeding/pull/220),
  [`8dbde33`](https://github.com/detailobsessed/copier-uv-bleeding/commit/8dbde33adbb6d9a0bc8a79afee0501ccf482377d))


## v0.27.11 (2026-02-13)

### Bug Fixes

- Add verbose=true to template update hook so prek shows the notice
  ([#216](https://github.com/detailobsessed/copier-uv-bleeding/pull/216),
  [`79a3518`](https://github.com/detailobsessed/copier-uv-bleeding/commit/79a35183064521bd84a4d2526d6955b04e28f710))

### Refactoring

- Add strict pylint and modern ruff rules to template
  ([#215](https://github.com/detailobsessed/copier-uv-bleeding/pull/215),
  [`e815632`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e8156327d61694329e96fc5d95c562848738773e))


## v0.27.10 (2026-02-12)

### Bug Fixes

- Tell python where .venv is explicitly to help code editors resolve modules
  ([#214](https://github.com/detailobsessed/copier-uv-bleeding/pull/214),
  [`82c75c2`](https://github.com/detailobsessed/copier-uv-bleeding/commit/82c75c2ef6214a7ee845214df55126a0f5f11fae))


## v0.27.9 (2026-02-12)

### Bug Fixes

- Use --only-group maintain in release job to minimize attack surface
  ([#213](https://github.com/detailobsessed/copier-uv-bleeding/pull/213),
  [`00daf7f`](https://github.com/detailobsessed/copier-uv-bleeding/commit/00daf7fab7d921015ac4a8427c6cce3f1a649774))


## v0.27.8 (2026-02-12)

### Bug Fixes

- Inline release logic, remove verify-scaffold.sh, fix CI continue-on-error, right-size triage
  runner ([#212](https://github.com/detailobsessed/copier-uv-bleeding/pull/212),
  [`421d227`](https://github.com/detailobsessed/copier-uv-bleeding/commit/421d227ca02aac39cb52525bc9ecebc4a66a28a9))


## v0.27.7 (2026-02-12)

### Bug Fixes

- Correct except syntax in check-pathlib-encoding and align setup-uv tags
  ([#211](https://github.com/detailobsessed/copier-uv-bleeding/pull/211),
  [`ad7a752`](https://github.com/detailobsessed/copier-uv-bleeding/commit/ad7a75294abc3480e380aaea5641f562f52c1e1e))


## v0.27.6 (2026-02-12)

### Bug Fixes

- Gitignore testmondata SQLite sidecar files
  ([#210](https://github.com/detailobsessed/copier-uv-bleeding/pull/210),
  [`5011a30`](https://github.com/detailobsessed/copier-uv-bleeding/commit/5011a30680d0e30ccd1065b245db3419932e78d8))


## v0.27.5 (2026-02-12)

### Bug Fixes

- Unblock .env.example.jinja from .gitignore and mark network-dependent tests as slow
  ([#209](https://github.com/detailobsessed/copier-uv-bleeding/pull/209),
  [`e30211d`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e30211daa54fcb0db233eca8a525570d63a2cf96))

### Chores

- Comment out COPIER_CHECK_INTERVAL in .env.example.jinja
  ([#208](https://github.com/detailobsessed/copier-uv-bleeding/pull/208),
  [`8eb44db`](https://github.com/detailobsessed/copier-uv-bleeding/commit/8eb44dbc4fcf4524f5cd43e982c70ae1b0cd99fe))

- Delete pr-description workflow — replaced by gt submit --ai
  ([#206](https://github.com/detailobsessed/copier-uv-bleeding/pull/206),
  [`091eb4a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/091eb4a4a24ac551c77a4ba2d4ada5a01f09cf54))

### Continuous Integration

- Consolidate test jobs into single test-project job
  ([#207](https://github.com/detailobsessed/copier-uv-bleeding/pull/207),
  [`140f950`](https://github.com/detailobsessed/copier-uv-bleeding/commit/140f9506363afd868a8c855f748d23f6e6df0dd6))


## v0.27.4 (2026-02-12)

### Bug Fixes

- Chmod scripts in _tasks to ensure executable bits after copier update
  ([#205](https://github.com/detailobsessed/copier-uv-bleeding/pull/205),
  [`27d688c`](https://github.com/detailobsessed/copier-uv-bleeding/commit/27d688c44b57dbc7c13b57f4e11ae2c1efb3f4ab))


## v0.27.3 (2026-02-12)

### Bug Fixes

- Set executable bit on check-template-update.sh
  ([#204](https://github.com/detailobsessed/copier-uv-bleeding/pull/204),
  [`4012488`](https://github.com/detailobsessed/copier-uv-bleeding/commit/4012488f43d7fc145eb06735e72686e15314e2d9))


## v0.27.2 (2026-02-12)

### Bug Fixes

- Use uv run for pathlib encoding check hook
  ([#203](https://github.com/detailobsessed/copier-uv-bleeding/pull/203),
  [`8810014`](https://github.com/detailobsessed/copier-uv-bleeding/commit/8810014e8ec6bd561859c283c2ac1ca17f906bf2))


## v0.27.1 (2026-02-11)

### Bug Fixes

- Add --no-cov to poe test-affected task
  ([#202](https://github.com/detailobsessed/copier-uv-bleeding/pull/202),
  [`e1eb54e`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e1eb54e68a2279129a51f11695b97e040eaa8d89))


## v0.27.0 (2026-02-11)

### Features

- Improve template update reliability + add pathlib encoding hook
  ([#200](https://github.com/detailobsessed/copier-uv-bleeding/pull/200),
  [`c917687`](https://github.com/detailobsessed/copier-uv-bleeding/commit/c9176876e4e98a51ad6031be0b0c74431a025800))


## v0.26.3 (2026-02-11)

### Bug Fixes

- Restore .git guard for prek install in copier _tasks
  ([#198](https://github.com/detailobsessed/copier-uv-bleeding/pull/198),
  [`de1d588`](https://github.com/detailobsessed/copier-uv-bleeding/commit/de1d5880e68037d5bbdcd88c6d5c680979449597))


## v0.26.2 (2026-02-11)

### Bug Fixes

- Modernize copier _tasks with _copier_operation and chain prek autoupdate
  ([#197](https://github.com/detailobsessed/copier-uv-bleeding/pull/197),
  [`1d50965`](https://github.com/detailobsessed/copier-uv-bleeding/commit/1d5096566e3a038c26823ec073c5c453b689c507))


## v0.26.1 (2026-02-11)

### Bug Fixes

- Make PR description check heading-agnostic
  ([#195](https://github.com/detailobsessed/copier-uv-bleeding/pull/195),
  [`560f77c`](https://github.com/detailobsessed/copier-uv-bleeding/commit/560f77cc8d29582097f31bb5e11143401f53165f))


## v0.26.0 (2026-02-11)

### Features

- Add PR description validation workflow and auto-create needs-triage label
  ([#194](https://github.com/detailobsessed/copier-uv-bleeding/pull/194),
  [`e35e840`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e35e840949a727a93db5866f5c38cdf9fb3568aa))


## v0.25.0 (2026-02-11)

### Bug Fixes

- Use uv sync --upgrade in post-copy tasks, add test-affected to scaffold check, mark slow tests
  ([#192](https://github.com/detailobsessed/copier-uv-bleeding/pull/192),
  [`1bd8dbb`](https://github.com/detailobsessed/copier-uv-bleeding/commit/1bd8dbbddc8865e7c8efd1e62c1391cc25cad3c7))

### Features

- Auto-create needs-triage label in issue triage workflow
  ([#193](https://github.com/detailobsessed/copier-uv-bleeding/pull/193),
  [`c19439b`](https://github.com/detailobsessed/copier-uv-bleeding/commit/c19439b681dd06b52a969458e079b9c3adfa5c94))


## v0.24.1 (2026-02-10)

### Bug Fixes

- Coverage inflation, GitLab badge check, release tag format
  ([#189](https://github.com/detailobsessed/copier-uv-bleeding/pull/189),
  [`e6228ab`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e6228aba25c9de249b44210459676a4bd524bf19))


## v0.24.0 (2026-02-10)

### Features

- Add pytest-testmon, improve post-apply experience
  ([#187](https://github.com/detailobsessed/copier-uv-bleeding/pull/187),
  [`979ffcd`](https://github.com/detailobsessed/copier-uv-bleeding/commit/979ffcd9104f948590f6abbd7b4718963f3bed9a))


## v0.23.0 (2026-02-10)

### Features

- Split README into user-owned starter + template-managed docs
  ([#182](https://github.com/detailobsessed/copier-uv-bleeding/pull/182),
  [`55e58aa`](https://github.com/detailobsessed/copier-uv-bleeding/commit/55e58aaa24979dbc785d95735994bc5a2065b70a))


## v0.22.1 (2026-02-10)

### Bug Fixes

- Switch template update hook from post-merge to post-checkout and add check-template task
  ([#179](https://github.com/detailobsessed/copier-uv-bleeding/pull/179),
  [`aaad053`](https://github.com/detailobsessed/copier-uv-bleeding/commit/aaad05329fea960d393c136f5c3e63e30d3df329))


## v0.22.0 (2026-02-10)

### Features

- Adopt poethepoet 0.38-0.41 features — parallel check task
  ([#174](https://github.com/detailobsessed/copier-uv-bleeding/pull/174),
  [`347c903`](https://github.com/detailobsessed/copier-uv-bleeding/commit/347c903e712bbffae35d3cf4a307a82c43d6c0f1))


## v0.21.0 (2026-02-10)

### Features

- Add post-merge hook to check for template updates
  ([#171](https://github.com/detailobsessed/copier-uv-bleeding/pull/171),
  [`7349eb7`](https://github.com/detailobsessed/copier-uv-bleeding/commit/7349eb744067c5dac93efdf737ea9181858bb71b))


## v0.20.4 (2026-02-10)

### Bug Fixes

- Gate PyPI links on publish_to_pypi, fix GitLab edit_uri, skip __init__.py on update, exclude
  overrides from lychee ([#169](https://github.com/detailobsessed/copier-uv-bleeding/pull/169),
  [`3170624`](https://github.com/detailobsessed/copier-uv-bleeding/commit/3170624c8d7bd589439214fc3c68a0ccf4cf89bd))

- Prevent race condition in pypi-publish by checking out release tag
  ([#163](https://github.com/detailobsessed/copier-uv-bleeding/pull/163),
  [`ff4c10f`](https://github.com/detailobsessed/copier-uv-bleeding/commit/ff4c10f0bcbbe5d13e1e0b2ae290a08808a3bf00))

- Trim default_install_hook_types to only hooks actually used
  ([#168](https://github.com/detailobsessed/copier-uv-bleeding/pull/168),
  [`64426d4`](https://github.com/detailobsessed/copier-uv-bleeding/commit/64426d477e76d2c46a6eb618ae6a042f55b2ed87))


## v0.20.3 (2026-02-08)

### Bug Fixes

- Include tests in ruff lint/format targets for generated projects
  ([#162](https://github.com/detailobsessed/copier-uv-bleeding/pull/162),
  [`3c166c2`](https://github.com/detailobsessed/copier-uv-bleeding/commit/3c166c2801428aa2622dd4e802422916f0655a0a))

### Documentation

- Add actionlint section to learning-tools.md
  ([#160](https://github.com/detailobsessed/copier-uv-bleeding/pull/160),
  [`1fef98d`](https://github.com/detailobsessed/copier-uv-bleeding/commit/1fef98dcfceecd3623a78277cb59d29c8b9025dd))

## v0.20.2 (2026-02-08)

### Bug Fixes

- Add id-token: write permission to release workflow for reusable workflow compatibility
  ([#158](https://github.com/detailobsessed/copier-uv-bleeding/pull/158),
  [`bdb718b`](https://github.com/detailobsessed/copier-uv-bleeding/commit/bdb718b04e731d90835faef3d7feafa1286bcb9a))

- Address post-merge review feedback from Devin
  ([#151](https://github.com/detailobsessed/copier-uv-bleeding/pull/151),
  [`81e2dc9`](https://github.com/detailobsessed/copier-uv-bleeding/commit/81e2dc9ff287016afd1bfd3c5e6253dba4d8982c))

- CI paths-filter permissions and lychee localhost exclusion
  ([#157](https://github.com/detailobsessed/copier-uv-bleeding/pull/157),
  [`81553e4`](https://github.com/detailobsessed/copier-uv-bleeding/commit/81553e4c2552753896948f8e4205d791e7a9f06d))

- Detect table-style poe tasks and fix issue triage workflow
  ([#154](https://github.com/detailobsessed/copier-uv-bleeding/pull/154),
  [`3b828e7`](https://github.com/detailobsessed/copier-uv-bleeding/commit/3b828e70f4ec38cc2aa7885da1c9c5013f8039bc))

- Pass dependency-group: dev to semantic-release workflow
  ([#159](https://github.com/detailobsessed/copier-uv-bleeding/pull/159),
  [`49c3516`](https://github.com/detailobsessed/copier-uv-bleeding/commit/49c3516888fca11278206a9f7b8a107f301788e1))

## v0.20.1 (2026-02-08)

### Bug Fixes

- CI path filter safety + pin lychee to stable release
  ([#150](https://github.com/detailobsessed/copier-uv-bleeding/pull/150),
  [`9b7a7f9`](https://github.com/detailobsessed/copier-uv-bleeding/commit/9b7a7f9d29fbfa6970c9f764bb2f8df70306151c))

## v0.20.0 (2026-02-08)

### Features

- Remove scaffold code, add issue templates, add no-commit-to-main hook
  ([#149](https://github.com/detailobsessed/copier-uv-bleeding/pull/149),
  [`4655885`](https://github.com/detailobsessed/copier-uv-bleeding/commit/465588509c7ec7b0c3d25e4cbdade29a4cbc13fc))

## v0.19.1 (2026-02-08)

### Performance Improvements

- Skip CI matrix for workflow-only changes
  ([#140](https://github.com/detailobsessed/copier-uv-bleeding/pull/140),
  [`bd24fb9`](https://github.com/detailobsessed/copier-uv-bleeding/commit/bd24fb96b0c61e2e9f1e406f89165bbdaa47484b))

## v0.19.0 (2026-02-08)

### Features

- Add sync-with-uv hook to generated projects
  ([#138](https://github.com/detailobsessed/copier-uv-bleeding/pull/138),
  [`9731ba1`](https://github.com/detailobsessed/copier-uv-bleeding/commit/9731ba12471684f542aa1046f1c111f13b59e718))

## v0.18.2 (2026-02-07)

### Bug Fixes

- Point sync-with-uv at fork with prek.toml support
  ([#137](https://github.com/detailobsessed/copier-uv-bleeding/pull/137),
  [`e87343e`](https://github.com/detailobsessed/copier-uv-bleeding/commit/e87343e23ee93ffcfc0f4f5365c80b6f7ffd2831))

## v0.18.1 (2026-02-07)

### Performance Improvements

- Speed up test suite with fixture caching and xdist
  ([#136](https://github.com/detailobsessed/copier-uv-bleeding/pull/136),
  [`bec58cf`](https://github.com/detailobsessed/copier-uv-bleeding/commit/bec58cfe05a9a0ba7e2d4160a87cc1e112a2e608))

## v0.18.0 (2026-02-07)

### Chores

- Migrate from tk to GitHub Issues
  ([#127](https://github.com/detailobsessed/copier-uv-bleeding/pull/127),
  [`b356e2a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/b356e2a217e9c8e82539f76498289f3581f640b6))

### Features

- Adjust lychee config for internal projects
  ([#131](https://github.com/detailobsessed/copier-uv-bleeding/pull/131),
  [`f88a6ef`](https://github.com/detailobsessed/copier-uv-bleeding/commit/f88a6efdd55aa000b1306bc71358b4e9b462ff29))

- Support self-hosted repository URLs (repository_host)
  ([#133](https://github.com/detailobsessed/copier-uv-bleeding/pull/133),
  [`4edbf8a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/4edbf8aa0ea8b72048d4074fa87b656546279928))

## v0.17.0 (2026-02-07)

### Features

- Add project_visibility question to gate open-source scaffolding
  ([#124](https://github.com/detailobsessed/copier-uv-bleeding/pull/124),
  [`1dc3b69`](https://github.com/detailobsessed/copier-uv-bleeding/commit/1dc3b697cc2daeacef888c2ce1888fd6a2c011b9))

## v0.16.6 (2026-02-07)

### Bug Fixes

- Add main.py to _skip_if_exists for app type adopt
  ([#123](https://github.com/detailobsessed/copier-uv-bleeding/pull/123),
  [`dc9147a`](https://github.com/detailobsessed/copier-uv-bleeding/commit/dc9147a3d6b136eaa8ea8caba96bf146e7d712d8))

## v0.16.5 (2026-02-07)

### Bug Fixes

- Lychee exclude_path for own config file + remove no_progress from generated projects
  ([#122](https://github.com/detailobsessed/copier-uv-bleeding/pull/122),
  [`176896b`](https://github.com/detailobsessed/copier-uv-bleeding/commit/176896bcb3498d3521f847e40c7632c47d9cd446))

## v0.16.4 (2026-02-07)

### Bug Fixes

- Exclude copier-update.yml when use_ci is false
  ([#121](https://github.com/detailobsessed/copier-uv-bleeding/pull/121),
  [`98b6382`](https://github.com/detailobsessed/copier-uv-bleeding/commit/98b638203e155fae719f4f9e2f5c8d54ee7043dd))

## v0.16.3 (2026-02-07)

### Bug Fixes

- Remove .vscode/ from template, standardize on .editorconfig
  ([#120](https://github.com/detailobsessed/copier-uv-bleeding/pull/120),
  [`26be11c`](https://github.com/detailobsessed/copier-uv-bleeding/commit/26be11c169b5ddc62f9d6b46eeeb4aefe343b668))

### Chores

- Add tk tickets for template audit findings and GH issue tracking
  ([#119](https://github.com/detailobsessed/copier-uv-bleeding/pull/119),
  [`abca985`](https://github.com/detailobsessed/copier-uv-bleeding/commit/abca9857e748dae1afd3fb6fedcd28ba133e1dee))

## v0.16.2 (2026-02-07)

### Bug Fixes

- Remove unconditional xdist, fix missing blank line before semantic_release (#113)
  ([#115](https://github.com/detailobsessed/copier-uv-bleeding/pull/115),
  [`43a62aa`](https://github.com/detailobsessed/copier-uv-bleeding/commit/43a62aa835aa4e279c54fd0e55d7f2af1eb11e16))

### Chores

- Migrate beads to tk for local issue tracking
  ([`49c51a4`](https://github.com/detailobsessed/copier-uv-bleeding/commit/49c51a4b915b3b7e4e9c90c826ca7a3c0f730bc7))

## v0.16.1 (2026-02-06)

### Bug Fixes

- Broken links and add lychee pre-commit hook
  ([#112](https://github.com/detailobsessed/copier-uv-bleeding/pull/112),
  [`4c00a6d`](https://github.com/detailobsessed/copier-uv-bleeding/commit/4c00a6de8fa994b99da160625f04687d639d40f3))

### Documentation

- Rewrite README, fix changelog marker + mode, fix CONTRIBUTING.md URL
  ([#110](https://github.com/detailobsessed/copier-uv-bleeding/pull/110),
  [`0390055`](https://github.com/detailobsessed/copier-uv-bleeding/commit/03900555902dba11d13d0c1f3d95bd5750b214e2))

### Refactoring

- Remove is_existing_project question — redundant with _skip_if_exists
  ([#111](https://github.com/detailobsessed/copier-uv-bleeding/pull/111),
  [`4032131`](https://github.com/detailobsessed/copier-uv-bleeding/commit/4032131b408b93073c233acd36131978597de69b))

## [1.11.2](https://github.com/pawamoy/copier-uv/releases/tag/1.11.2) - 2025-11-20

<small>[Compare with 1.11.1](https://github.com/pawamoy/copier-uv/compare/1.11.1...1.11.2)</small>

### Code Refactoring

- Stop using mkdocs-material-insiders ([0d015fe](https://github.com/pawamoy/copier-uv/commit/0d015fe2510c0c0ba1ac3c9b51132d127a733569) by Timothée Mazzucotelli).

## [1.11.1](https://github.com/pawamoy/copier-uv/releases/tag/1.11.1) - 2025-11-08

<small>[Compare with 1.11.0](https://github.com/pawamoy/copier-uv/compare/1.11.0...1.11.1)</small>

### Bug Fixes

- Fix tagging commit when signed commits are enabled? ([f1f0950](https://github.com/pawamoy/copier-uv/commit/f1f095096134da1dbd0f1d138303938db7b81405) by Timothée Mazzucotelli).
- Always force docs deployment ([c41b8fe](https://github.com/pawamoy/copier-uv/commit/c41b8fe3e80aef11539191ad903d2b8d3f8419fd) by Timothée Mazzucotelli).

### Code Refactoring

- Remove Insiders-related contents ([79737bf](https://github.com/pawamoy/copier-uv/commit/79737bff38ac2e3d8e0aa98a80a2742627db3506) by Timothée Mazzucotelli).

## [1.11.0](https://github.com/pawamoy/copier-uv/releases/tag/1.11.0) - 2025-10-24

<small>[Compare with 1.10.2](https://github.com/pawamoy/copier-uv/compare/1.10.2...1.11.0)</small>

### Features

- Automate sponsors update in README ([7ab74bd](https://github.com/pawamoy/copier-uv/commit/7ab74bda37e88600207c899fd28fa0f94f335422) by Timothée Mazzucotelli).

### Bug Fixes

- Use specific version of artifact ([91b5c99](https://github.com/pawamoy/copier-uv/commit/91b5c99eb81bcdb826a04cbc7ab61c2042a09552) by Timothée Mazzucotelli).

### Code Refactoring

- Remove match parameter on test duty, since we can pass `-k` directly ([ca104e4](https://github.com/pawamoy/copier-uv/commit/ca104e43275bf60020550c57bcfec92d755a1f11) by Timothée Mazzucotelli).
- Remove support for Python 3.9, add support for Python 3.14, add testing for Python 3.15 ([946ca5a](https://github.com/pawamoy/copier-uv/commit/946ca5a172c51bcd0e64aa93c990327f453a8110) by Timothée Mazzucotelli).
- Use Python 3.13 in non-matrix jobs ([9256040](https://github.com/pawamoy/copier-uv/commit/925604062ba14b901b3791182b3fe260a96ea888) by Timothée Mazzucotelli).
- Upgrade setup-python action to v6 ([86a942d](https://github.com/pawamoy/copier-uv/commit/86a942d8c7ac134d35ef9fc741ce9113fd75e77e) by Timothée Mazzucotelli).

## [1.10.2](https://github.com/pawamoy/copier-uv/releases/tag/1.10.2) - 2025-10-09

<small>[Compare with 1.10.1](https://github.com/pawamoy/copier-uv/compare/1.10.1...1.10.2)</small>

### Bug Fixes

- Fix CI workflow ([4f874da](https://github.com/pawamoy/copier-uv/commit/4f874da228df372601820a32550345b6156947de) by Timothée Mazzucotelli). [Issue-78](https://github.com/pawamoy/copier-uv/issues/78)

## [1.10.1](https://github.com/pawamoy/copier-uv/releases/tag/1.10.1) - 2025-10-09

<small>[Compare with 1.10.0](https://github.com/pawamoy/copier-uv/compare/1.10.0...1.10.1)</small>

### Bug Fixes

- Fix typo in PR template ([b270abc](https://github.com/pawamoy/copier-uv/commit/b270abcd8a4cf25819ac2dbed5de9aa506dfea07) by Timothée Mazzucotelli).

## [1.10.0](https://github.com/pawamoy/copier-uv/releases/tag/1.10.0) - 2025-10-07

<small>[Compare with 1.9.0](https://github.com/pawamoy/copier-uv/compare/1.9.0...1.10.0)</small>

### Features

- Warn on default encoding in `open()` calls ([f41edb4](https://github.com/pawamoy/copier-uv/commit/f41edb4bf2955944f41905db003ceb3414707286) by Bartosz Sławecki). [PR-77](https://github.com/pawamoy/copier-uv/pull/77)
- Run quality CI on matrix ([27ffb20](https://github.com/pawamoy/copier-uv/commit/27ffb20707594ae9e8d3c18cee67b8750cff8b66) by Bartosz Sławecki). [PR-73](https://github.com/pawamoy/copier-uv/pull/73)
- Don't run CI on topic branches without a PR ([0c4f6cd](https://github.com/pawamoy/copier-uv/commit/0c4f6cd4cf5a00e67ec64d61078c8b0cc8891e87) by Bartosz Sławecki). [PR-71](https://github.com/pawamoy/copier-uv/pull/71)
- Cancel no longer useful runs in the same PR ([34b8778](https://github.com/pawamoy/copier-uv/commit/34b8778f63a3986d26a521917658c7057541ab51) by Bartosz Sławecki). [PR-74](https://github.com/pawamoy/copier-uv/pull/74)

### Code Refactoring

- Support light and dark background logos for premium sponsors ([852105a](https://github.com/pawamoy/copier-uv/commit/852105a6c5fc57f456b4f11b44badff9c939c3cc) by Timothée Mazzucotelli).
- Don't fail fast ([bce6109](https://github.com/pawamoy/copier-uv/commit/bce61095c99a0b95f89f0edfa9a2a616580b7084) by Bartosz Sławecki). [PR-75](https://github.com/pawamoy/copier-uv/pull/75)

## [1.9.0](https://github.com/pawamoy/copier-uv/releases/tag/1.9.0) - 2025-09-01

<small>[Compare with 1.8.9](https://github.com/pawamoy/copier-uv/compare/1.8.9...1.9.0)</small>

### Features

- Print file:lineno in API test output ([fce4ee4](https://github.com/pawamoy/copier-uv/commit/fce4ee494b095fdd998f00a695b93580e5518917) by Timothée Mazzucotelli).
- Add pull request template ([5f60cf1](https://github.com/pawamoy/copier-uv/commit/5f60cf1c6b25490c0798e1b3d5e661160f78a993) by Timothée Mazzucotelli).

## [1.8.9](https://github.com/pawamoy/copier-uv/releases/tag/1.8.9) - 2025-08-15

<small>[Compare with 1.8.8](https://github.com/pawamoy/copier-uv/compare/1.8.8...1.8.9)</small>

### Code Refactoring

- Be more resilient to errors in latest (dev) Python version ([898db72](https://github.com/pawamoy/copier-uv/commit/898db72f88f12707452727afcd60701c7f7d433c) by Timothée Mazzucotelli).
- Remove Radicle badge extension (too bothersome, will add badges manually) ([1e2dbfd](https://github.com/pawamoy/copier-uv/commit/1e2dbfdeaa6891d2204ad192bd60e43d702a6d4a) by Timothée Mazzucotelli).

## [1.8.8](https://github.com/pawamoy/copier-uv/releases/tag/1.8.8) - 2025-08-15

<small>[Compare with 1.8.7](https://github.com/pawamoy/copier-uv/compare/1.8.7...1.8.8)</small>

### Code Refactoring

- Debug Radicle ID context hook ([d8069b9](https://github.com/pawamoy/copier-uv/commit/d8069b9990c86dcba61ac88cd09d0d4c1613b1fc) by Timothée Mazzucotelli).

## [1.8.7](https://github.com/pawamoy/copier-uv/releases/tag/1.8.7) - 2025-08-15

<small>[Compare with 1.8.6](https://github.com/pawamoy/copier-uv/compare/1.8.6...1.8.7)</small>

### Code Refactoring

- Take control over the Gitter/Matrix badge's color ([a8f9282](https://github.com/pawamoy/copier-uv/commit/a8f92822ddc4bc607cba12bfbf0de8e99faf3a14) by Timothée Mazzucotelli).
- Add a `rad clone` badge if the repository was `rad init`'d ([ee65aee](https://github.com/pawamoy/copier-uv/commit/ee65aee0375d4a381dbd9e59f4d9b525c9ca5b6b) by Timothée Mazzucotelli).

## [1.8.6](https://github.com/pawamoy/copier-uv/releases/tag/1.8.6) - 2025-07-15

<small>[Compare with 1.8.5](https://github.com/pawamoy/copier-uv/compare/1.8.5...1.8.6)</small>

### Code Refactoring

- Use new package name for extensions ([27c1d8e](https://github.com/pawamoy/copier-uv/commit/27c1d8e8b2e55c2b2c7e78af13c655fa5c5ccb08) by Timothée Mazzucotelli).
- Improve initial output of `make` ([ac0da32](https://github.com/pawamoy/copier-uv/commit/ac0da32484365a593b79b98acf25301704653223) by Timothée Mazzucotelli). [PR-griffe-393](https://github.com/mkdocstrings/griffe/pull/393)

## [1.8.5](https://github.com/pawamoy/copier-uv/releases/tag/1.8.5) - 2025-07-03

<small>[Compare with 1.8.4](https://github.com/pawamoy/copier-uv/compare/1.8.4...1.8.5)</small>

### Code Refactoring

- Ignore Ruff/ty warnings, prepare ty use ([d581cd6](https://github.com/pawamoy/copier-uv/commit/d581cd6164a82c47924e908a6287b4cfde850412) by Timothée Mazzucotelli).

## [1.8.4](https://github.com/pawamoy/copier-uv/releases/tag/1.8.4) - 2025-04-08

<small>[Compare with 1.8.3](https://github.com/pawamoy/copier-uv/compare/1.8.3...1.8.4)</small>

### Code Refactoring

- Format code (new Ruff lints) ([17b874f](https://github.com/pawamoy/copier-uv/commit/17b874f39aecb2400bb2b6a8ed1cc6fb5a92b525) by Timothée Mazzucotelli).

## [1.8.3](https://github.com/pawamoy/copier-uv/releases/tag/1.8.3) - 2025-04-08

<small>[Compare with 1.8.2](https://github.com/pawamoy/copier-uv/compare/1.8.2...1.8.3)</small>

### Code Refactoring

- Update usage of mkdocs-llmstxt ([93ac1bb](https://github.com/pawamoy/copier-uv/commit/93ac1bb40cf161c0200165b30a3c3f3389a8dce3) by Timothée Mazzucotelli).

## [1.8.2](https://github.com/pawamoy/copier-uv/releases/tag/1.8.2) - 2025-03-24

<small>[Compare with 1.8.1](https://github.com/pawamoy/copier-uv/compare/1.8.1...1.8.2)</small>

### Bug Fixes

- Exclude mypy cache folders from sdists ([16011cc](https://github.com/pawamoy/copier-uv/commit/16011cc9c6f3149c03e6c8c3362ecf32160c2bca) by Timothée Mazzucotelli).

## [1.8.1](https://github.com/pawamoy/copier-uv/releases/tag/1.8.1) - 2025-03-13

<small>[Compare with 1.8.0](https://github.com/pawamoy/copier-uv/compare/1.8.0...1.8.1)</small>

### Code Refactoring

- Improve API tests robustness ([65a867c](https://github.com/pawamoy/copier-uv/commit/65a867c77f4f244c10b5def1fa5d75eaefaba6bb) by Timothée Mazzucotelli).

## [1.8.0](https://github.com/pawamoy/copier-uv/releases/tag/1.8.0) - 2025-03-11

<small>[Compare with 1.7.1](https://github.com/pawamoy/copier-uv/compare/1.7.1...1.8.0)</small>

### Features

- Enable backlinks in API docs ([20aba08](https://github.com/pawamoy/copier-uv/commit/20aba086f2bfe7939bedce9d0fa457a19089159a) by Timothée Mazzucotelli).

### Code Refactoring

- Fully enable autorefs for docs ([152924d](https://github.com/pawamoy/copier-uv/commit/152924dcc5b8238f016abe89297a6402ec779bd8) by Timothée Mazzucotelli).
- Simplify API docs (stop using gen-files and literate-nav) ([6d1aec8](https://github.com/pawamoy/copier-uv/commit/6d1aec8c12673b10192903f584d40ddc94741dbf) by Timothée Mazzucotelli).

## [1.7.1](https://github.com/pawamoy/copier-uv/releases/tag/1.7.1) - 2025-03-02

<small>[Compare with 1.7.0](https://github.com/pawamoy/copier-uv/compare/1.7.0...1.7.1)</small>

### Bug Fixes

- Output llms-full.txt, not llms.txt ([2c8b4f8](https://github.com/pawamoy/copier-uv/commit/2c8b4f8d55d7e66d8c14c0ec897828d065969fb5) by Timothée Mazzucotelli).

## [1.7.0](https://github.com/pawamoy/copier-uv/releases/tag/1.7.0) - 2025-03-01

<small>[Compare with 1.6.4](https://github.com/pawamoy/copier-uv/compare/1.6.4...1.7.0)</small>

### Features

- Check legacy code with Yore each time the changelog is updated ([63e4af5](https://github.com/pawamoy/copier-uv/commit/63e4af5bd318c1625e4f51e9a5d24a7b941d7277) by Timothée Mazzucotelli). [Issue-60](https://github.com/pawamoy/copier-uv/issues/60)
- Split dependency-groups in sections ([bae928e](https://github.com/pawamoy/copier-uv/commit/bae928ece555c14ac8eae8e1ad4b7c0d6f98faf0) by Dennis Bücker). [Discussion-58](https://github.com/pawamoy/copier-uv/discussions/58), [PR-59](https://github.com/pawamoy/copier-uv/pull/59)

## [1.6.4](https://github.com/pawamoy/copier-uv/releases/tag/1.6.4) - 2025-02-24

<small>[Compare with 1.6.3](https://github.com/pawamoy/copier-uv/compare/1.6.3...1.6.4)</small>

### Code Refactoring

- Stop depending on Black now that mkdocstrings-python supports Ruff for formatting signatures ([6554451](https://github.com/pawamoy/copier-uv/commit/65544511a65dc075157ee3f3686882108e93ed6d) by Timothée Mazzucotelli).

## [1.6.3](https://github.com/pawamoy/copier-uv/releases/tag/1.6.3) - 2025-02-24

<small>[Compare with 1.6.2](https://github.com/pawamoy/copier-uv/compare/1.6.2...1.6.3)</small>

### Bug Fixes

- Ensure test jobs wait for quality one (for objects inventory artifact to be ready) ([885f204](https://github.com/pawamoy/copier-uv/commit/885f204f5b32b43099193cd2f7cc62e4011f39b0) by Timothée Mazzucotelli).

## [1.6.2](https://github.com/pawamoy/copier-uv/releases/tag/1.6.2) - 2025-02-24

<small>[Compare with 1.6.1](https://github.com/pawamoy/copier-uv/compare/1.6.1...1.6.2)</small>

### Code Refactoring

- Store and download objects inventory in CI, enabling API tests ([a55906c](https://github.com/pawamoy/copier-uv/commit/a55906c88042e454547af8a5ee0e946e3ef57d6e) by Timothée Mazzucotelli).

## [1.6.1](https://github.com/pawamoy/copier-uv/releases/tag/1.6.1) - 2025-02-19

<small>[Compare with 1.6.0](https://github.com/pawamoy/copier-uv/compare/1.6.0...1.6.1)</small>

### Bug Fixes

- Fix license choices in template configuration ([f26c221](https://github.com/pawamoy/copier-uv/commit/f26c22184aa6326f94a6722dc818b7364e8bb8bc) by Timothée Mazzucotelli).

## [1.6.0](https://github.com/pawamoy/copier-uv/releases/tag/1.6.0) - 2025-02-19

<small>[Compare with 1.5.7](https://github.com/pawamoy/copier-uv/compare/1.5.7...1.6.0)</small>

### Features

- Generate /llms.txt docs file ([2000ef6](https://github.com/pawamoy/copier-uv/commit/2000ef688cc75e71140a6acecf9fd918ee9210b6) by Timothée Mazzucotelli). [Issue-49](https://github.com/pawamoy/copier-uv/issues/49)
- Add initial API tests ([997155b](https://github.com/pawamoy/copier-uv/commit/997155b69ba48d397433582127302696c08dbb0e) by Timothée Mazzucotelli).
- Add config to run project, and allow to pass arguments ([bd88519](https://github.com/pawamoy/copier-uv/commit/bd8851921c7105aa523867e7f64a217a562a5a41) by Timothée Mazzucotelli). [Issue-53](https://github.com/pawamoy/copier-uv/issues/53)

### Bug Fixes

- Prevent extension crash with key error ([1d27caf](https://github.com/pawamoy/copier-uv/commit/1d27caf9d79919c1e4d97cb312b19e80bc947d59) by Timothée Mazzucotelli).

### Code Refactoring

- Prevent publishing insiders packages to PyPI ([b51ae0f](https://github.com/pawamoy/copier-uv/commit/b51ae0f48257a83279e97a7adb2c6a240139383b) by Timothée Mazzucotelli). [Issue-44](https://github.com/pawamoy/copier-uv/issues/44)
- Mention `insiders` instead of `pypi-insiders` in docs ([4c8d09e](https://github.com/pawamoy/copier-uv/commit/4c8d09e914b4e88d9522f4aafb37b9aabd22c780) by Timothée Mazzucotelli). [Issue-45](https://github.com/pawamoy/copier-uv/issues/45)
- Write comments, not docstrings in internal modules/scripts ([bedf879](https://github.com/pawamoy/copier-uv/commit/bedf8796b76b215c5d228d6b76f5fa22c7a0eddc) by Timothée Mazzucotelli).
- Use an "internal" layout ([fd500cc](https://github.com/pawamoy/copier-uv/commit/fd500cc25be5b0a169153b08b0715a5c21715f00) by Timothée Mazzucotelli). [Issue-50](https://github.com/pawamoy/copier-uv/issues/50)
- Remove Ko-Fi and Paypal from funding file ([16f0e0e](https://github.com/pawamoy/copier-uv/commit/16f0e0e8e48bbf8ec7ac1864f3bf54271faab9c0) by Timothée Mazzucotelli). [Issue-55](https://github.com/pawamoy/copier-uv/issues/55)
- Update setup-uv action version ([52df1c1](https://github.com/pawamoy/copier-uv/commit/52df1c14eed14bc08a3e5d6cb92112376c44d136) by Timothée Mazzucotelli). [Issue-54](https://github.com/pawamoy/copier-uv/issues/54)
- Enable docs instant preview (link hover) ([59b1229](https://github.com/pawamoy/copier-uv/commit/59b12297d085aeac5d7187c5f2c98e91ce60ba7e) by Timothée Mazzucotelli). [Issue-52](https://github.com/pawamoy/copier-uv/issues/52)
- Rename mkdocstrings-python `import` option to `inventories` ([c56d1cc](https://github.com/pawamoy/copier-uv/commit/c56d1cc58f4fc357582ee4e17885c11f53e5c200) by Timothée Mazzucotelli).
- Enable docs navigation breadcrumbs ([15536d7](https://github.com/pawamoy/copier-uv/commit/15536d76e5482bd4ec9738345142e13e5b91f953) by Timothée Mazzucotelli).
- Rename script that generates API reference ([db1a856](https://github.com/pawamoy/copier-uv/commit/db1a856081b5d0540ad3823cb54299191722c6b7) by Timothée Mazzucotelli).
- Set metadata title in docs pages ([1837a07](https://github.com/pawamoy/copier-uv/commit/1837a07b751964de44631211dbfa7154ec33a547) by Timothée Mazzucotelli).
- Update license templating ([84537c7](https://github.com/pawamoy/copier-uv/commit/84537c7ea157c9f5876f626e4a7d92619348a915) by Timothée Mazzucotelli).
- Update insiders docs now that we better handle beneficiaries ([59bbbb5](https://github.com/pawamoy/copier-uv/commit/59bbbb5334ce0362537e0737df6e38d73f461339) by Timothée Mazzucotelli).

## [1.5.7](https://github.com/pawamoy/copier-uv/releases/tag/1.5.7) - 2025-01-23

<small>[Compare with 1.5.6](https://github.com/pawamoy/copier-uv/compare/1.5.6...1.5.7)</small>

### Bug Fixes

- Preserve symlinks (make -> make.py) ([dab1219](https://github.com/pawamoy/copier-uv/commit/dab12193b3651001e10dab56b0ff72aacfcdf3c7) by Timothée Mazzucotelli).

### Code Refactoring

- Enable Mypy colored output ([c6622f8](https://github.com/pawamoy/copier-uv/commit/c6622f8e1dc2bb94860c1f3ef4dc9305bbc87422) by Timothée Mazzucotelli).

## [1.5.6](https://github.com/pawamoy/copier-uv/releases/tag/1.5.6) - 2024-12-24

<small>[Compare with 1.5.5](https://github.com/pawamoy/copier-uv/compare/1.5.5...1.5.6)</small>

### Code Refactoring

- Fallback onto finding current project version in CHANGELOG.md when Git tags give 0.1 or less ([da5df83](https://github.com/pawamoy/copier-uv/commit/da5df834ce79ff3d7920f914adccc746a4d9e5af) by Timothée Mazzucotelli).

## [1.5.5](https://github.com/pawamoy/copier-uv/releases/tag/1.5.5) - 2024-12-23

<small>[Compare with 1.5.4](https://github.com/pawamoy/copier-uv/compare/1.5.4...1.5.5)</small>

### Bug Fixes

- Ignore constraints on main package (from dependencies), to allow resolving deps in forks/CI ([d644679](https://github.com/pawamoy/copier-uv/commit/d644679a3e6370244f7e7893dfdbd1d776288096) by Timothée Mazzucotelli). [Issue-uv#8148](https://github.com/astral-sh/uv/issues/8148)

### Code Refactoring

- Always disable re-sync when using `uv run` through `make` ([3fe244b](https://github.com/pawamoy/copier-uv/commit/3fe244b9b3540425323024b0def9b715b9648c4f) by Timothée Mazzucotelli).
- Remove default PDM settings from pyproject.toml, use default pth-type editable installs ([d6ef6f8](https://github.com/pawamoy/copier-uv/commit/d6ef6f81b94396a4c4f375ee39228bf5e6d40534) by Timothée Mazzucotelli).

## [1.5.4](https://github.com/pawamoy/copier-uv/releases/tag/1.5.4) - 2024-11-21

<small>[Compare with 1.5.3](https://github.com/pawamoy/copier-uv/compare/1.5.3...1.5.4)</small>

### Code Refactoring

- Declare dev-deps using PEP 735 ([79f05ef](https://github.com/pawamoy/copier-uv/commit/79f05efe32f73c57b44fa9a3bebe9cbf108176b7) by Timothée Mazzucotelli). [Issue-42](https://github.com/pawamoy/copier-uv/issues/42)

## [1.5.3](https://github.com/pawamoy/copier-uv/releases/tag/1.5.3) - 2024-11-11

<small>[Compare with 1.5.2](https://github.com/pawamoy/copier-uv/compare/1.5.2...1.5.3)</small>

### Bug Fixes

- Don't pass `--python python` to uv, which requires a `python` exec in the PATH ([331db66](https://github.com/pawamoy/copier-uv/commit/331db66178682d9f310280a7ead6bd6d6ca3dbf5) by Timothée Mazzucotelli). [Issue-40](https://github.com/pawamoy/copier-uv/issues/40)
- Make it so that linters see the make script ([4989d1e](https://github.com/pawamoy/copier-uv/commit/4989d1e628bac45472ffc6b8deaa2879765cde5c) by Timothée Mazzucotelli).

### Code Refactoring

- Improve experience for Windows users ([ece7662](https://github.com/pawamoy/copier-uv/commit/ece7662adab1408d6206740cece7b9cd2206bd6e) by Blair Conrad). [PR-33](https://github.com/pawamoy/copier-uv/pull/33)

## [1.5.2](https://github.com/pawamoy/copier-uv/releases/tag/1.5.2) - 2024-10-17

<small>[Compare with 1.5.1](https://github.com/pawamoy/copier-uv/compare/1.5.1...1.5.2)</small>

### Bug Fixes

- Also remove Gitpod badge since we removed configuration ([65cc91a](https://github.com/pawamoy/copier-uv/commit/65cc91a26231944e8cfd338ff2fca1d6b9db4d7f) by Timothée Mazzucotelli).
- Only add `force` parameter to docs-deploy duty when insiders is enabled ([8df12ae](https://github.com/pawamoy/copier-uv/commit/8df12ae770ffee8f2966fa8aae41e01125c6250e) by Timothée Mazzucotelli).

## [1.5.1](https://github.com/pawamoy/copier-uv/releases/tag/1.5.1) - 2024-10-12

<small>[Compare with 1.5.0](https://github.com/pawamoy/copier-uv/compare/1.5.0...1.5.1)</small>

### Bug Fixes

- Always fetch the whole Git history, needed to build the current project in non-editable mode with an up-to-date version ([f52522e](https://github.com/pawamoy/copier-uv/commit/f52522e0d611f6d4fb5d8c8b8c16925b651ad700) by Timothée Mazzucotelli).

## [1.5.0](https://github.com/pawamoy/copier-uv/releases/tag/1.5.0) - 2024-10-12

<small>[Compare with 1.4.8](https://github.com/pawamoy/copier-uv/compare/1.4.8...1.5.0)</small>

### Features

- Allow forcing docs deployment ([b8f0b63](https://github.com/pawamoy/copier-uv/commit/b8f0b636355151e0b14edf58de688884f789c513) by Timothée Mazzucotelli).

## [1.4.8](https://github.com/pawamoy/copier-uv/releases/tag/1.4.8) - 2024-10-11

<small>[Compare with 1.4.7](https://github.com/pawamoy/copier-uv/compare/1.4.7...1.4.8)</small>

### Code Refactoring

- Enable PyO3 ABI3 forward compatibility when installing deps ([c391679](https://github.com/pawamoy/copier-uv/commit/c39167913b4493bc951b2d2c693a7efcc2af1834) by Timothée Mazzucotelli).

## [1.4.7](https://github.com/pawamoy/copier-uv/releases/tag/1.4.7) - 2024-10-11

<small>[Compare with 1.4.6](https://github.com/pawamoy/copier-uv/compare/1.4.6...1.4.7)</small>

### Code Refactoring

- Drop support for Python 3.8, start testing on Python 3.14 ([f24adfe](https://github.com/pawamoy/copier-uv/commit/f24adfe8209db336526b8a819088ff40fdc88a27) by Timothée Mazzucotelli).
- Use newest uv features, `uv run --no-sync` and `uv sync --no-editable` ([ad2ab81](https://github.com/pawamoy/copier-uv/commit/ad2ab8145193affc6442dd36aa8e6867cb234c3e) by Timothée Mazzucotelli).
- More uses of uv in docs ([0e3300e](https://github.com/pawamoy/copier-uv/commit/0e3300ec0f4c28546fbce52e34fc7e8d11bba28d) by Timothée Mazzucotelli).
- Remove GitPod configuration ([977fe75](https://github.com/pawamoy/copier-uv/commit/977fe754314039c1774d996d91baf0b409dc0237) by Timothée Mazzucotelli).

## [1.4.6](https://github.com/pawamoy/copier-uv/releases/tag/1.4.6) - 2024-10-07

<small>[Compare with 1.4.5](https://github.com/pawamoy/copier-uv/compare/1.4.5...1.4.6)</small>

### Bug Fixes

- Use uv to fix pip installs breaking system Python in GHA ([b86d3e9](https://github.com/pawamoy/copier-uv/commit/b86d3e99c34224a5203ac295b34deaa12d85fba2) by Timothée Mazzucotelli).

## [1.4.5](https://github.com/pawamoy/copier-uv/releases/tag/1.4.5) - 2024-09-27

<small>[Compare with 1.4.4](https://github.com/pawamoy/copier-uv/compare/1.4.4...1.4.5)</small>

### Bug Fixes

- Fix make help message indentation ([addb51e](https://github.com/pawamoy/copier-uv/commit/addb51ed8daaeb19d40cd02665f8fc68bb02f4b8) by Timothée Mazzucotelli).
- Invalidate uv cache based on pyproject.toml ([b78ce88](https://github.com/pawamoy/copier-uv/commit/b78ce880c56b3e346d5b414bda89ac4a8cd22335) by Timothée Mazzucotelli).

## [1.4.4](https://github.com/pawamoy/copier-uv/releases/tag/1.4.4) - 2024-09-27

<small>[Compare with 1.4.3](https://github.com/pawamoy/copier-uv/compare/1.4.3...1.4.4)</small>

### Code Refactoring

- Upgrade setup-uv action version ([cc2c350](https://github.com/pawamoy/copier-uv/commit/cc2c350d6f2c42025ed84afa5740a767ff82510b) by Timothée Mazzucotelli).

## [1.4.3](https://github.com/pawamoy/copier-uv/releases/tag/1.4.3) - 2024-09-27

<small>[Compare with 1.4.2](https://github.com/pawamoy/copier-uv/compare/1.4.2...1.4.3)</small>

### Code Refactoring

- Upgrade gh-release action version ([d26e9fa](https://github.com/pawamoy/copier-uv/commit/d26e9fa99f715e41642d26a32403fc934da4391d) by Timothée Mazzucotelli).

## [1.4.2](https://github.com/pawamoy/copier-uv/releases/tag/1.4.2) - 2024-09-27

<small>[Compare with 1.4.1](https://github.com/pawamoy/copier-uv/compare/1.4.1...1.4.2)</small>

### Bug Fixes

- Better flush help message for make script ([fb2d373](https://github.com/pawamoy/copier-uv/commit/fb2d373b217c1d3c216b01f82e3db5c2f1542558) by Timothée Mazzucotelli).
- Better handle `gh` command error (when fetching "Documentation" category ID for discussions) ([896dfb3](https://github.com/pawamoy/copier-uv/commit/896dfb39ea6710b3965fd3162fa9b621f916d166) by Timothée Mazzucotelli).

### Code Refactoring

- Update ci and release workflows ([4692788](https://github.com/pawamoy/copier-uv/commit/46927885db4aad4658802707d1f34a129633b83e) by Timothée Mazzucotelli).

## [1.4.1](https://github.com/pawamoy/copier-uv/releases/tag/1.4.1) - 2024-09-05

<small>[Compare with 1.4.0](https://github.com/pawamoy/copier-uv/compare/1.4.0...1.4.1)</small>

### Bug Fixes

- Disallow overrides when getting Git remote in docs-deploy duty ([cb0135b](https://github.com/pawamoy/copier-uv/commit/cb0135bf5bc80768fea17366efba35293c60ba93) by Timothée Mazzucotelli).

### Code Refactoring

- Improve clean command ([d4dfab7](https://github.com/pawamoy/copier-uv/commit/d4dfab790dee59c335ac8907afd468a2cddd0169) by Timothée Mazzucotelli).
- Enable Git revision date docs plugin, remove Git committers plugin (vendor lock-in, requires GitHub token) ([c4907eb](https://github.com/pawamoy/copier-uv/commit/c4907eb96914914314bedf55d300179a790b827a) by Timothée Mazzucotelli).
- Don't show source code in docs when insiders ([5c57d92](https://github.com/pawamoy/copier-uv/commit/5c57d9213b22e3cebec01d3557ea779695bd50da) by Timothée Mazzucotelli).
- Clean up `check` duty (pre tasks) ([2e4dd5b](https://github.com/pawamoy/copier-uv/commit/2e4dd5b65ff49e45a6123a701ae572a6a15041aa) by Timothée Mazzucotelli).
- Use higher-level uv commands ([bf3c328](https://github.com/pawamoy/copier-uv/commit/bf3c328b8aefa1b5e33bb3bf55ff0039c9a436b1) by Timothée Mazzucotelli).

## [1.4.0](https://github.com/pawamoy/copier-uv/releases/tag/1.4.0) - 2024-07-04

<small>[Compare with 1.3.0](https://github.com/pawamoy/copier-uv/compare/1.3.0...1.4.0)</small>

### Features

- Add feedback system using Giscus ([a69ab13](https://github.com/pawamoy/copier-uv/commit/a69ab13feddbe7fb6f12f3b1d93dda18ecedef30) by Timothée Mazzucotelli).

### Code Refactoring

- Rephrase announcement ([bc48d13](https://github.com/pawamoy/copier-uv/commit/bc48d139e806d656674848cb0e174902e8f0174d) by Timothée Mazzucotelli).
- Add note about lower sponsorships ([6a2d804](https://github.com/pawamoy/copier-uv/commit/6a2d8042ed48cba6f763a040e53ba8135b148d16) by Timothée Mazzucotelli).

## [1.3.0](https://github.com/pawamoy/copier-uv/releases/tag/1.3.0) - 2024-06-26

<small>[Compare with 1.2.11](https://github.com/pawamoy/copier-uv/compare/1.2.11...1.3.0)</small>

### Features

- Add docs update and change request issue templates ([8f41407](https://github.com/pawamoy/copier-uv/commit/8f41407d7cb626ff00e9269c62c287628f67ae5c) by Timothée Mazzucotelli). [Issue-27](https://github.com/pawamoy/copier-uv/issues/27)

### Bug Fixes

- Fix make script to be compatible with Python < 3.10 ([795f39f](https://github.com/pawamoy/copier-uv/commit/795f39f42a51a9ecb8c316e8dc5546a56e4e2f8f) by Timothée Mazzucotelli).
- Update contributing docs (mention `make` script instead of Makefile) ([7e76e47](https://github.com/pawamoy/copier-uv/commit/7e76e47fed603703b0fd6868dca4b318cb0c585c) by Timothée Mazzucotelli). [Issue-28](https://github.com/pawamoy/copier-uv/issues/28)

## [1.2.11](https://github.com/pawamoy/copier-uv/releases/tag/1.2.11) - 2024-06-26

<small>[Compare with 1.2.10](https://github.com/pawamoy/copier-uv/compare/1.2.10...1.2.11)</small>

### Bug Fixes

- Make sure to print errors in case of failure of `make` command ([54696f3](https://github.com/pawamoy/copier-uv/commit/54696f3ced18fee3b6d7262989f9f97b5d2218ea) by Timothée Mazzucotelli). [Issue-26](https://github.com/pawamoy/copier-uv/issues/26)
- Make sure `setup` returns non-0 exit code when uv fails to resolve dependencies ([ba5c4dc](https://github.com/pawamoy/copier-uv/commit/ba5c4dcc8128afa06abd1d2c679c263e4761fd59) by Timothée Mazzucotelli).
- Fix Twine dependency (5.1 has been yanked) ([e022917](https://github.com/pawamoy/copier-uv/commit/e022917f40db2e82c07f5b4a3e2eb31f947c48a6) by Timothée Mazzucotelli).

## [1.2.10](https://github.com/pawamoy/copier-uv/releases/tag/1.2.10) - 2024-06-18

<small>[Compare with 1.2.9](https://github.com/pawamoy/copier-uv/compare/1.2.9...1.2.10)</small>

### Code Refactoring

- Include almost everything in source distributions, to help system packagers ([064ffb0](https://github.com/pawamoy/copier-uv/commit/064ffb06b5f0e2039987116e443f67cf877965d1) by Timothée Mazzucotelli).

## [1.2.9](https://github.com/pawamoy/copier-uv/releases/tag/1.2.9) - 2024-06-14

<small>[Compare with 1.2.8](https://github.com/pawamoy/copier-uv/compare/1.2.8...1.2.9)</small>

### Bug Fixes

- Re-include tests folder in source distributions ([3d9a7e1](https://github.com/pawamoy/copier-uv/commit/3d9a7e17167294ee43673cafa615931614240235) by Timothée Mazzucotelli).

## [1.2.8](https://github.com/pawamoy/copier-uv/releases/tag/1.2.8) - 2024-05-24

<small>[Compare with 1.2.7](https://github.com/pawamoy/copier-uv/compare/1.2.7...1.2.8)</small>

### Bug Fixes

- Fix calling tasks from actual Makefile ([30d3bc9](https://github.com/pawamoy/copier-uv/commit/30d3bc91d01d59d7b0ef10b7a5a3f77bd64543a2) by Timothée Mazzucotelli).

## [1.2.7](https://github.com/pawamoy/copier-uv/releases/tag/1.2.7) - 2024-05-23

<small>[Compare with 1.2.6](https://github.com/pawamoy/copier-uv/compare/1.2.6...1.2.7)</small>

### Code Refactoring

- Rename `cov` duty to `coverage` (keep `cov` as alias) ([0bb541b](https://github.com/pawamoy/copier-uv/commit/0bb541bd5910b0fdaf8018fd0a7b3fda563958b8) by Timothée Mazzucotelli).
- Format make script again, add docstrings and type annotations ([e754b45](https://github.com/pawamoy/copier-uv/commit/e754b455c54fe61925d046e16a50ef8580e75eb5) by Timothée Mazzucotelli).

## [1.2.6](https://github.com/pawamoy/copier-uv/releases/tag/1.2.6) - 2024-05-23

<small>[Compare with 1.2.5](https://github.com/pawamoy/copier-uv/compare/1.2.5...1.2.6)</small>

### Code Refactoring

- Reformat make script ([734f664](https://github.com/pawamoy/copier-uv/commit/734f6641dc360a04e19e00dfc090778eb66d9f2c) by Timothée Mazzucotelli).

## [1.2.5](https://github.com/pawamoy/copier-uv/releases/tag/1.2.5) - 2024-05-23

<small>[Compare with 1.2.4](https://github.com/pawamoy/copier-uv/compare/1.2.4...1.2.5)</small>

### Code Refactoring

- Remove pip self-hosted solution from insiders installation docs ([1743f52](https://github.com/pawamoy/copier-uv/commit/1743f521db021a345107f4f3f865d0ad2f1d5817) by Timothée Mazzucotelli).
- Rewrite make script in Python ([67fcd8b](https://github.com/pawamoy/copier-uv/commit/67fcd8bc08943dc437b7e0aa072786e88a0882ea) by Timothée Mazzucotelli).
- Rewrite duties using the new duty "tools" ([7d5a690](https://github.com/pawamoy/copier-uv/commit/7d5a690306c77772370f5715478d3f9d1f1a9cd9) by Timothée Mazzucotelli).
- Clean up pytest config ([1151e7d](https://github.com/pawamoy/copier-uv/commit/1151e7dd9f627d431116f5620e219239b8649107) by Timothée Mazzucotelli).
- Upgrade minimum versions of dev-deps ([b1622e9](https://github.com/pawamoy/copier-uv/commit/b1622e9f3ae3464dfb01dc1de73afa6312015626) by Timothée Mazzucotelli).
- Remove check-dependencies task for now ([618922f](https://github.com/pawamoy/copier-uv/commit/618922fe21e745d2ef121aaf8032352118d09429) by Timothée Mazzucotelli).

## [1.2.4](https://github.com/pawamoy/copier-uv/releases/tag/1.2.4) - 2024-04-26

<small>[Compare with 1.2.3](https://github.com/pawamoy/copier-uv/compare/1.2.3...1.2.4)</small>

### Bug Fixes

- Super final ultimate fix for publish duty ([f888d9f](https://github.com/pawamoy/copier-uv/commit/f888d9fc312dbdc3fb51227de2cc3d11191bd8b9) by Timothée Mazzucotelli).

## [1.2.3](https://github.com/pawamoy/copier-uv/releases/tag/1.2.3) - 2024-04-26

<small>[Compare with 1.2.2](https://github.com/pawamoy/copier-uv/compare/1.2.2...1.2.3)</small>

### Bug Fixes

- Further fixes to release/publish duties ([263580a](https://github.com/pawamoy/copier-uv/commit/263580a69cb725e0bf927c6cda5598f372087b73) by Timothée Mazzucotelli).

## [1.2.2](https://github.com/pawamoy/copier-uv/releases/tag/1.2.2) - 2024-04-26

<small>[Compare with 1.2.1](https://github.com/pawamoy/copier-uv/compare/1.2.1...1.2.2)</small>

### Bug Fixes

- Don't use modern annotations as duty fails evaluating them on Python 3.8 and 3.9 ([4cd01f9](https://github.com/pawamoy/copier-uv/commit/4cd01f9d6e5f4f866dc1b3ffe8f7f39ab407e2ba) by Timothée Mazzucotelli).

## [1.2.1](https://github.com/pawamoy/copier-uv/releases/tag/1.2.1) - 2024-04-26

<small>[Compare with 1.2.0](https://github.com/pawamoy/copier-uv/compare/1.2.0...1.2.1)</small>

### Bug Fixes

- Only print available tasks if venvs are setup ([0c65bdf](https://github.com/pawamoy/copier-uv/commit/0c65bdf186498fc701162d37a2029aba5760b867) by Timothée Mazzucotelli).
- Fix build and publish duties ([27eb549](https://github.com/pawamoy/copier-uv/commit/27eb5490128131c6681d4bb15d84950f8d971296) by Timothée Mazzucotelli).

## [1.2.0](https://github.com/pawamoy/copier-uv/releases/tag/1.2.0) - 2024-04-26

<small>[Compare with 1.1.0](https://github.com/pawamoy/copier-uv/compare/1.1.0...1.2.0)</small>

### Features

- Add `build` and `publish` duties ([5b4e70a](https://github.com/pawamoy/copier-uv/commit/5b4e70aac58c6633f4546a0784aedbe32f0e9576) by Timothée Mazzucotelli).
- Allow passing a `bump` value to the changelog duty ([2a1e535](https://github.com/pawamoy/copier-uv/commit/2a1e535818ddc990f7320277e77f1f3a06056a59) by Timothée Mazzucotelli).
- Allow passing release version interactively ([6839286](https://github.com/pawamoy/copier-uv/commit/6839286cf868a3bebcc91c4e62f8942c4c0496c3) by Timothée Mazzucotelli).
- All `allrun` and `3.x` commands to make script ([25c7e1b](https://github.com/pawamoy/copier-uv/commit/25c7e1b05ff12dfaf17074bdddb46ce222f027ab) by Timothée Mazzucotelli). [Issue-12](https://github.com/pawamoy/copier-uv/issues/12)
- Run tests with direct dependencies resolved to their lowest version ([339e2c6](https://github.com/pawamoy/copier-uv/commit/339e2c64c2ce542eff513324d7ab2100f816548f) by Timothée Mazzucotelli). [Issue-22](https://github.com/pawamoy/copier-uv/issues/22)

### Bug Fixes

- Don't include current project in credits ([77ae955](https://github.com/pawamoy/copier-uv/commit/77ae955bde1f5816eb6f2d83a0d5645643b33dfc) by Timothée Mazzucotelli). [Issue-18](https://github.com/pawamoy/copier-uv/issues/18)
- Fix parsing options in make scripts ([4dbb47c](https://github.com/pawamoy/copier-uv/commit/4dbb47cf0c308b4a2b405ed7300dbbf5523b0df5) by Timothée Mazzucotelli). [Issue-21](https://github.com/pawamoy/copier-uv/issues/21)

### Code Refactoring

- Prepare inclusion of manpages when building dists ([0a1151c](https://github.com/pawamoy/copier-uv/commit/0a1151caa2212ab1004db26766d25790f11d0d49) by Timothée Mazzucotelli).
- Use PEP 440 versioning scheme for changelog ([3f3a3c6](https://github.com/pawamoy/copier-uv/commit/3f3a3c6581278af39ca25ff6a53b27b7391e3000) by Timothée Mazzucotelli).
- Transform non Python tasks into make commands ([1b29786](https://github.com/pawamoy/copier-uv/commit/1b297864602c193c836603b9e90cd8c92ff75840) by Timothée Mazzucotelli).
- Sort credits case-insensitively ([459caf0](https://github.com/pawamoy/copier-uv/commit/459caf09e3709523cc0170823652be5a96777e34) by Timothée Mazzucotelli). [Issue-10](https://github.com/pawamoy/copier-uv/issues/10)
- Improve dev-deps, improve credits script ([c199b30](https://github.com/pawamoy/copier-uv/commit/c199b3049469b463299b42fac68299a77bd9fad8) by Timothée Mazzucotelli).
- Update badges ([5dba46f](https://github.com/pawamoy/copier-uv/commit/5dba46fa15cf04ad28b733bf1d61152e5166217a) by Timothée Mazzucotelli). [Issue-13](https://github.com/pawamoy/copier-uv/issues/13)
- Use current color for autorefs arrows ([f5e8745](https://github.com/pawamoy/copier-uv/commit/f5e8745879186c03bbe623f8347fb0580951c7c8) by Timothée Mazzucotelli). [Issue-19](https://github.com/pawamoy/copier-uv/issues/19)
- Add front-matter title to auto-generated reference pages ([8f33202](https://github.com/pawamoy/copier-uv/commit/8f33202840ea561f39ae7ab567eed8c8098baef0) by Timothée Mazzucotelli). [Issue-20](https://github.com/pawamoy/copier-uv/issues/20)
- Test on Python 3.13 ([e7806d9](https://github.com/pawamoy/copier-uv/commit/e7806d9e0358351496c1a9759c5d5f7d393744aa) by Timothée Mazzucotelli). [Issue-23](https://github.com/pawamoy/copier-uv/issues/23)
- uv is now able to install unnamed projects ([647579a](https://github.com/pawamoy/copier-uv/commit/647579a3cf33a42d373b86d35892b730ce70bdb6) by Timothée Mazzucotelli).

## [1.1.0](https://github.com/pawamoy/copier-uv/releases/tag/1.1.0) - 2024-03-19

<small>[Compare with 1.0.8](https://github.com/pawamoy/copier-uv/compare/1.0.8...1.1.0)</small>

### Features

- Add Python interpreter path to debug information ([9ab5feb](https://github.com/pawamoy/copier-uv/commit/9ab5feb3455302c0384a7c7ed42490e23fff10f1) by Timothée Mazzucotelli). [Issue-1](https://github.com/pawamoy/copier-uv/issues/1)
- Add Polar to funding file ([9e6c75f](https://github.com/pawamoy/copier-uv/commit/9e6c75f491725cb78626e3bf64bd78234f7bc4c8) by Timothée Mazzucotelli). [Issue-3](https://github.com/pawamoy/copier-uv/issues/3)

### Bug Fixes

- Fix issues with credits generation ([7384022](https://github.com/pawamoy/copier-uv/commit/73840229fc5be3106a71354e33a910b1e996161c) by Timothée Mazzucotelli). [Issue-4](https://github.com/pawamoy/copier-uv/issues/4)
- Correctly exclude fixtures from Ruff ([2dcda18](https://github.com/pawamoy/copier-uv/commit/2dcda18c230c0584a24e54fdf6098c4559716800) by Timothée Mazzucotelli). [Issue-6](https://github.com/pawamoy/copier-uv/issues/6)

### Code Refactoring

- Improve .gitignore and clean duty ([0590438](https://github.com/pawamoy/copier-uv/commit/0590438d94757ba2e672908cafdb0d0fef4aca96) by Timothée Mazzucotelli). [Issue-5](https://github.com/pawamoy/copier-uv/issues/5)
- Handle local/CI installation in `make setup` ([bddbbba](https://github.com/pawamoy/copier-uv/commit/bddbbbaf5915c60e35370dfa1316633ba802e980) by Timothée Mazzucotelli). [Issue-8](https://github.com/pawamoy/copier-uv/issues/8)
- Don't install pip, wheel and setuptools in venvs ([e423892](https://github.com/pawamoy/copier-uv/commit/e4238920184c5ba337adbbe3e0cf5ada44cd26c5) by Timothée Mazzucotelli). [Issue-9](https://github.com/pawamoy/copier-uv/issues/9)

## [1.0.8](https://github.com/pawamoy/copier-uv/releases/tag/1.0.8) - 2024-03-13

<small>[Compare with 1.0.7](https://github.com/pawamoy/copier-uv/compare/1.0.7...1.0.8)</small>

### Bug Fixes

- Remove prefix from completed goals HTML ids ([3e1d865](https://github.com/pawamoy/copier-uv/commit/3e1d865c27c48fb760a96928055e64460dcab765) by Timothée Mazzucotelli).

### Code Refactoring

- Link to global goal when there are no features ([fe6c538](https://github.com/pawamoy/copier-uv/commit/fe6c5382672f7c57b50de091c0af6aca9d4ffdfc) by Timothée Mazzucotelli).
- Prepare goal names ([fe89ca7](https://github.com/pawamoy/copier-uv/commit/fe89ca781f3c9758b61573cb5490183fd0661b13) by Timothée Mazzucotelli).

## [1.0.7](https://github.com/pawamoy/copier-uv/releases/tag/1.0.7) - 2024-03-13

<small>[Compare with 1.0.6](https://github.com/pawamoy/copier-uv/compare/1.0.6...1.0.7)</small>

### Code Refactoring

- Update premium sponsors display ([aabb40a](https://github.com/pawamoy/copier-uv/commit/aabb40aa4bae70b7b431f8857069e3a4ddc37fbc) by Timothée Mazzucotelli).

## [1.0.6](https://github.com/pawamoy/copier-uv/releases/tag/1.0.6) - 2024-03-02

<small>[Compare with 1.0.5](https://github.com/pawamoy/copier-uv/compare/1.0.5...1.0.6)</small>

### Code Refactoring

- Improve Insiders features paragraph ([8179314](https://github.com/pawamoy/copier-uv/commit/81793149195d112676c9b222510655f37955d6c9) by Timothée Mazzucotelli).

## [1.0.5](https://github.com/pawamoy/copier-uv/releases/tag/1.0.5) - 2024-02-29

<small>[Compare with 1.0.4](https://github.com/pawamoy/copier-uv/compare/1.0.4...1.0.5)</small>

### Bug Fixes

- Fix view/edit URIs in docs ([8fdf5dd](https://github.com/pawamoy/copier-uv/commit/8fdf5dd1192f5a868eb484e5bbc020e9c9b1d16a) by Timothée Mazzucotelli).

## [1.0.4](https://github.com/pawamoy/copier-uv/releases/tag/1.0.4) - 2024-02-28

<small>[Compare with 1.0.3](https://github.com/pawamoy/copier-uv/compare/1.0.3...1.0.4)</small>

### Bug Fixes

- I AM SO ANNOYED BY THIS OS ([2c5beb4](https://github.com/pawamoy/copier-uv/commit/2c5beb4f341f510ebb7d04ab29a02cf99c46195e) by Timothée Mazzucotelli).
- Fix dependencies installation in CI ([af33aab](https://github.com/pawamoy/copier-uv/commit/af33aabbbf75e8f76e05b82d20f8ac3f4cbb51aa) by Timothée Mazzucotelli).

## [1.0.3](https://github.com/pawamoy/copier-uv/releases/tag/1.0.3) - 2024-02-28

<small>[Compare with 1.0.2](https://github.com/pawamoy/copier-uv/compare/1.0.2...1.0.3)</small>

### Bug Fixes

- Fix parsing options now that the script exits on errors ([c800738](https://github.com/pawamoy/copier-uv/commit/c8007383ecfbb8edb54af31d54a0e136c82cb758) by Timothée Mazzucotelli).

## [1.0.2](https://github.com/pawamoy/copier-uv/releases/tag/1.0.2) - 2024-02-28

<small>[Compare with 1.0.1](https://github.com/pawamoy/copier-uv/compare/1.0.1...1.0.2)</small>

### Bug Fixes

- Fix uv install and credits again ([7ce4e3b](https://github.com/pawamoy/copier-uv/commit/7ce4e3b56c678637acc030655b13d6a87b30f0bd) by Timothée Mazzucotelli).

## [1.0.1](https://github.com/pawamoy/copier-uv/releases/tag/1.0.1) - 2024-02-28

<small>[Compare with 1.0.0](https://github.com/pawamoy/copier-uv/compare/1.0.0...1.0.1)</small>

### Bug Fixes

- Fix credits generation, preventing dev-deps to appear as runtime ones ([dfa6ed4](https://github.com/pawamoy/copier-uv/commit/dfa6ed40ab7caaa7aa475d6d48f3fbbaf8c32b38) by Timothée Mazzucotelli).
- Fix re-installation of deps ([ace356a](https://github.com/pawamoy/copier-uv/commit/ace356a0cea6bf6d074af8a8bbe35e846661abf0) by Timothée Mazzucotelli).

### Code Refactoring

- Update Ruff config file ([71713de](https://github.com/pawamoy/copier-uv/commit/71713defd32eb6e8597c90279fe23171a470c2e8) by Timothée Mazzucotelli).
- Clean up config files ([a9d58ac](https://github.com/pawamoy/copier-uv/commit/a9d58ac5a39ea043605d060e4863e6c36bbc0f8a) by Timothée Mazzucotelli).

## [1.0.0](https://github.com/pawamoy/copier-uv/releases/tag/1.0.0) - 2024-02-19

<small>[Compare with first commit](https://github.com/pawamoy/copier-uv/compare/ad5932b04cecfcc6e6d1311f10082289cbc6ed76...1.0.0)</small>

### Features

- Make it work with uv ([469fc45](https://github.com/pawamoy/copier-uv/commit/469fc459f04786c0064d746e778ef799e9a9eabc) by Timothée Mazzucotelli).
- Fork from [Copier PDM v1.2.3](https://copier-pdm.github.io/copier-pdm/changelog/#123-2024-02-11)
