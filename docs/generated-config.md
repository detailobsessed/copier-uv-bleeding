# Why the generated config looks like this

Most of `pyproject.toml` in a generated project is ordinary. A handful of
settings are not, and look wrong or removable until you know what they defend
against. Every one of them exists because something broke.

The generated file carries a one-line pointer to the relevant section here
rather than the full explanation — the reasoning is template history, not
something every new project should inherit in its own config.

## Build backend

### Why `uv_build` is pinned to a window {#build-backend-pin}

```toml
requires = ["uv_build>=0.12,<0.13"]
```

An unbounded `uv_build` makes uv warn on every `uv sync` and `uv build`, and a
breaking `uv_build` release would silently break sdist builds in every project
generated from this template at once. The bound is the current minor series
plus the next major; bump the window when `uv_build` crosses it (DOT-589).

The window moved to the `0.12` series for uv 0.12, which enforces PEP 625:
source distributions must be `.tar.gz`, and `.tar.bz2` / `.tar.xz` are
rejected, as are wheels using bzip2/LZMA/XZ compression. `uv_build` already
emits PEP 625-conforming artifacts, so the move was a no-op for generated
projects — verified by building an sdist and a wheel from a rendered project
under `uv_build` 0.12 and installing the result.

## Dependencies

### Why the dependency floors are tight {#dependency-floors}

Floors in `[dependency-groups]` track the versions this template is actually
exercised against, not the oldest release that happens to still work.

A range wider than the tested one advertises support nobody verifies: `uv sync`
resolves to the newest release, so the bottom of a `>=8` range is a
configuration the template has never once run under. `ty` is floored tighter
than the rest because it is pre-1.0, where any release may change behaviour.

## Ruff

### Why `required-version` is set {#ruff-required-version}

```toml
required-version = ">=0.16"
```

The `extend-select` list assumes ruff 0.16's broad defaults (413 rules). On
0.14 and 0.15 the defaults are just 59 rules (E4/E7/E9/F), so extending them
would silently drop the prefixes deleted from the list as redundant — `DTZ`,
`FA`, `FLY` and `PIE` — with no warning at all. Failing loudly is the better
trade.

This lives in `[tool.ruff]` rather than only in the `ci` dependency floor
because that group sits inside a [template-preserve region](update.md): a
project updating from an older template keeps its own `ruff>=0.14` but does
receive this section, so the floor alone would not protect it.

### Why preview rules are off {#ruff-preview}

```toml
preview = false
```

Preview rules are unstable by definition — they change behaviour and can be
removed between patch releases, which would turn a routine ruff upgrade into a
broken lint run for every template user.

Turning preview on also opts into preview-only config syntax that then cannot
be turned off again:

- `rule-codes-in-selectors` (RUF201) demands rule *names* in ignore selectors,
  but names are themselves rejected outside preview
  (`Selecting rules by name requires preview mode`).
- `noqa-comments` demands `# ruff: ignore[...]`, which stable ruff does not
  honour as a suppression at all.

Rule codes and `# noqa:` work in both modes, so they are the portable choice.
Stable ruff 0.16 already enables 413 rules.

### Why `extend-select` and not `select` {#ruff-extend-select}

Ruff's default rule set is broad (413 rules as of 0.16) and grows with each
release. `select` **replaces** that set, so a curated list silently switches off
every default it omits — the list this template used to ship was disabling 81
of them, including all ten flake8-async rules, blind-except, the leftover-
debugger check and the flake8-pyi rules, with nothing warning that it was doing
so.

`extend-select` layers on top of the defaults instead, so future ruff releases
add coverage rather than quietly losing it.

Only list a prefix in `extend-select` if it is **not** already on by default.
Entries that become default should be deleted rather than kept "for
documentation": a redundant entry is indistinguishable from a load-bearing one.

## Semantic release

These apply only when `use_semantic_release` is enabled.

### Why `build_command` starts with `set -e` {#semantic-release-build-command}

python-semantic-release hands `build_command` to the shell as a *script*, not
as an `&&` chain. Without `set -e` a failing `uv lock` is swallowed: the
remaining lines still run, `uv build` exits 0, and the release reports success
having committed a stale lockfile.

CI cannot catch this afterwards either, because the generated workflow runs
`uv sync --frozen`, which uses the lockfile as-is rather than asserting it is
fresh (`--locked` is the flag that would). DOT-602.

### Why `build_command` unsets empty `UV_*` variables {#semantic-release-unset-guards}

```sh
[ -n "$UV_SYSTEM_CERTS" ] || unset UV_SYSTEM_CERTS
```

Bare entries in `build_command_env` are resolved as `os.getenv(name, "")` and
assigned unconditionally, so a variable that is unset in CI arrives as an empty
string rather than being omitted.

uv parses its own `UV_*` variables as typed CLI values — an enum for
`--link-mode`, a path for `--cache-dir`, a boolish for `--system-certs` — so an
empty one is a *malformed* value, not an absent one, and `uv lock` exits 2
before doing any work.

The TLS and proxy variables are read as plain strings where empty already means
unset, so they need no guard. Each of the twelve was verified individually
against uv 0.12.1. DOT-615.

**Any new `UV_*` entry added to `build_command_env` needs a matching guard.**

### Why `build_command_env` exists at all {#semantic-release-build-command-env}

python-semantic-release **replaces** the environment for `build_command`
instead of extending it: it builds a hardcoded allowlist (`PATH`, `HOME`,
`VIRTUAL_ENV`, `CI`, `GITHUB_ACTIONS`, …) and passes it to `shell()` as `env=`.
Everything else is dropped.

Since `build_command` runs `uv lock`, which is a network operation, it would
otherwise execute with no TLS, proxy or cache configuration while every other
job in the same pipeline has all of it. This inverts the usual CI intuition
that exporting a variable in the job is enough. DOT-605.

A bare `"VAR"` entry is pass-through; `"VAR=value"` sets a literal.

Keep the proxy variables as a set: `HTTPS_PROXY` without `NO_PROXY` routes
internal hosts through the corporate proxy, which is the failure mode this
replaces. `SSL_CERT_DIR` is included alongside `SSL_CERT_FILE` because uv 0.12
made an invalid value in either one a hard HTTPS failure rather than a
warning-and-fall-back.

## Hooks

These cover `prek.toml` and `_typos.toml`.

### Why `minimum_prek_version` is pinned {#prek-minimum-version}

prek 0.4.10 introduced the `[update]` tag filters used to exclude lychee's
`nightly` tag. That version floor is the guard that reaches projects updating
from an older template: `prek.toml` is regenerated in full by the template's
[sync step](update.md), but `[dependency-groups]` in `pyproject.toml` sits
inside a template-preserve region, so the `prek>=` floor there stays at
whatever the project already had.

A too-old prek would otherwise ignore the `[update]` block entirely and
silently reintroduce the lychee bug below. `minimum_prek_version` fails loudly
instead. DOT-616.

### Why lychee's `nightly` tag is excluded from updates {#prek-lychee-nightly}

```toml
[update.repos."https://github.com/lycheeverse/lychee"]
exclude_tags = ["nightly"]
```

lychee tags `nightly` as their GitHub "Latest" release, so `prek update`
resolves it as the newest tag and rewrites the pinned rev to a mutable one that
lychee's own hook then rejects
([lycheeverse/lychee#1601](https://github.com/lycheeverse/lychee/issues/1601),
DOT-492).

Declaring the exclusion in config rather than wrapping `prek update` in a
script means every invocation is protected — a bare `prek update`, CI, an
editor integration — not just the one that goes through the wrapper (DOT-616).
Remove once upstream fixes it (DOT-504).

### Why `rev` lines must not carry trailing comments {#prek-rev-lines}

Empty `rev` values are filled by `prek update` and kept in step with `uv.lock`
by the `sync-with-uv` hook. That hook matches revs with a regex anchored at
end-of-line, so a trailing comment on a `rev` line makes it unmatchable — and
the hook then silently reports success while updating nothing. DOT-603.

Put per-repo notes on the line *above* the `rev`.

### Why the `typos` hook overrides `args` {#prek-typos-args}

Upstream ships `args = ["--write-changes", "--force-exclude"]`, so the hook
rewrites files in place. It has silently corrupted hex identifiers — Mongo
ObjectIds, git SHAs — in checked-in data files (DOT-604).

Overriding `args` **replaces** the upstream list rather than appending to it,
which is what drops the write flag. Keep `--force-exclude`: it is what makes
typos honour `_typos.toml` when prek passes explicit staged filenames instead
of letting typos walk the tree.

### Why `_typos.toml` excludes generated files {#typos-exclusions}

Release tooling writes abbreviated git SHAs, which typos reads as prose
(`ba` → `by`/`be`).

`.copier-answers.yml` is the same problem with worse consequences. Copier
writes `_commit: <git describe>` there, e.g. `0.41.3-3-g2452caf` — and short
SHAs are hex, so any of the handful of words spellable from `[0-9a-f]` trips
the dictionary: `caf`, `beef`, `fade`, `dead`, `deca`. That makes it fail on a
minority of commits and pass on the rest, which is close to impossible to
diagnose from the outside.

Worse, `_commit` is what `copier update` reads to find the template revision to
diff against; a "corrected" SHA points at nothing and breaks updates for the
project entirely.

When adding your own exclusions — data files holding hex-like identifiers, JSON
exports, fixtures, snapshots are the usual reason — prefer a path exclusion
over a repo-wide hex `extend-ignore-re`, which would also silence real typos in
source and docs.

### Why copier conflict markers get their own guards {#prek-copier-conflicts}

Two hooks exist because `copier update` can leave conflict debris that a normal
commit would otherwise carry into history:

- `check-merge-conflict` runs with `--assume-in-merge`, which catches markers
  left by `copier update --conflict inline`. Without the flag the hook skips
  the check, because there is no `.git/MERGE_MSG` outside a real merge.
- `no-copier-rej-files` blocks commits containing `.rej` files produced by
  `copier update --conflict rej` (DOT-542). See Copier's
  [tips and tricks](https://copier.readthedocs.io/en/stable/updating/#tips-and-tricks).
