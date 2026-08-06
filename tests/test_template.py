"""Comprehensive tests for copier template generation."""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import stat
import subprocess
import tomllib
from typing import TYPE_CHECKING, ClassVar

import pytest
import yaml
from conftest import REPO_ROOT, generate_project

if TYPE_CHECKING:
    from pathlib import Path


class TestProjectTypes:
    """Test project types (app = CLI, lib = no CLI)."""

    def test_app_type_has_cli(self, copier_defaults: dict, project_factory) -> None:
        """App type should have CLI entry point."""
        project = project_factory(copier_defaults, "app")

        pyproject = project / "pyproject.toml"
        assert pyproject.exists()

        content = pyproject.read_text()
        assert "[project.scripts]" in content
        assert "test-project" in content  # CLI name from slugified project_name

    def test_lib_type_no_cli(self, copier_defaults: dict, project_factory) -> None:
        """Library type should not have CLI entry point."""
        project = project_factory(copier_defaults, "lib")

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[project.scripts]" not in content

    def test_no_main_py(self, copier_defaults: dict, project_factory) -> None:
        """Neither type should generate main.py (users create their own)."""
        for project_type in ("app", "lib"):
            project = project_factory(copier_defaults, project_type)
            assert not (project / "main.py").exists()


class TestCoreFiles:
    """Test core files are generated correctly."""

    def test_pyproject_toml_exists(self, copier_defaults: dict, project_factory) -> None:
        """pyproject.toml should exist."""
        project = project_factory(copier_defaults)
        assert (project / "pyproject.toml").exists()

    def test_precommit_config_exists(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should exist."""
        project = project_factory(copier_defaults)
        assert (project / "prek.toml").exists()

    def test_ruff_config_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Ruff config should be in pyproject.toml."""
        project = project_factory(copier_defaults)
        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.ruff]" in content
        assert "[tool.ruff.lint]" in content

    def test_ruff_extends_defaults_rather_than_replacing_them(self, copier_defaults: dict, project_factory) -> None:
        """Ruff config must use `extend-select`, never `select`.

        `select` REPLACES ruff's default rule set; `extend-select` layers on
        top of it. Ruff's defaults are broad (413 rules as of 0.16) and grow
        with each release, so a curated `select` list silently switches off
        every default it happens to omit — and nothing warns that it has.
        Before this was fixed the template disabled 81 default rules that way,
        including every flake8-async rule, blind-except and the leftover
        debugger check.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            lint = tomllib.load(f)["tool"]["ruff"]["lint"]

        assert "select" not in lint, (
            "`select` replaces ruff's defaults, silently disabling every rule it omits. "
            "Use `extend-select` so new ruff defaults are added rather than dropped."
        )
        assert "extend-select" in lint, "ruff config should declare extend-select"

    def test_ruff_does_not_select_default_rules(self, copier_defaults: dict, project_factory) -> None:
        """Prefixes that ruff now enables by default should not be re-listed.

        A redundant entry is indistinguishable from a load-bearing one, so they
        get deleted rather than kept "for documentation". These four are fully
        covered by stable ruff 0.16's defaults.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            selected = tomllib.load(f)["tool"]["ruff"]["lint"]["extend-select"]

        redundant = sorted({"DTZ", "FA", "FLY", "PIE"} & set(selected))
        assert not redundant, f"these prefixes are fully enabled by ruff's defaults; drop them: {redundant!r}"

    def test_ruff_required_version_matches_the_extend_select_premise(self, copier_defaults: dict, project_factory) -> None:
        """`extend-select` is only safe on ruff >=0.16, so the config must demand it.

        Ruff 0.14/0.15 enable 59 default rules (E4/E7/E9/F); 0.16 enables 413.
        The four prefixes deleted as "redundant" are covered by the 413 and not
        by the 59, so on an older ruff `extend-select` drops them silently.

        `required-version` is the load-bearing guard rather than the `ci`
        dependency floor: that group lives inside a `template-preserve` region,
        so a project updating from an older template keeps its own `ruff>=0.14`
        while still receiving this `[tool.ruff]` section. Only a constraint
        inside the propagated section protects it, and it fails loudly.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)

        assert data["tool"]["ruff"].get("required-version") == ">=0.16", (
            "extend-select assumes ruff 0.16's 413 default rules; without required-version "
            "an older ruff silently drops DTZ/FA/FLY/PIE instead of failing"
        )

        ci_deps = data["dependency-groups"]["ci"]
        ci_ruff = next((spec for spec in ci_deps if spec.startswith("ruff>=")), None)
        assert ci_ruff is not None, f"the ci group must floor ruff; got {ci_deps!r}"
        # The ci floor tracks the tested version and may sit *above* required-version
        # (which is pinned to the minor whose defaults `extend-select` assumes). It must
        # never sit below it, or a resolvable install would hard-fail on required-version.
        parts = tuple(int(p) for p in ci_ruff.removeprefix("ruff>=").split("."))
        assert parts >= (0, 16), f"the ci floor must not fall below required-version; got {ci_ruff!r}"

    def test_ruff_preview_is_disabled(self, copier_defaults: dict, project_factory) -> None:
        """Generated projects must not opt into ruff's preview rules.

        Preview rules are unstable by contract: they change behaviour and can
        be withdrawn between patch releases. That is a poor default to hand to
        someone who adopted this template for a real project — a routine ruff
        upgrade turns into new lint failures they did not ask for.

        Stable ruff 0.16 already enables 413 rules, so preview buys very little
        coverage for the churn it adds.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            ruff = tomllib.load(f)["tool"]["ruff"]

        assert ruff.get("preview") is False, (
            "preview must be explicitly disabled — leaving it on subjects generated "
            "projects to rules that can change or vanish in a patch release."
        )

    def test_ruff_selectors_use_rule_codes(self, copier_defaults: dict, project_factory) -> None:
        """Ignore selectors must use rule codes, not rule names.

        This is load-bearing, not cosmetic. Rule names in a selector are
        rejected outside preview mode ("Selecting rules by name requires
        preview mode"), so switching the ignore lists to names silently pins
        the template to `preview = true` forever. Codes are accepted in both
        modes; names are a one-way door.

        Category prefixes in `select` (`E`, `PLR`) are not affected.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            lint = tomllib.load(f)["tool"]["ruff"]["lint"]

        selectors = list(lint.get("ignore", []))
        for ignores in lint.get("per-file-ignores", {}).values():
            selectors.extend(ignores)

        names = [s for s in selectors if not re.fullmatch(r"[A-Z]+[0-9]*", s)]
        assert not names, (
            f"rule names in ignore selectors require preview mode, which this template "
            f"deliberately disables. Use the rule codes instead. Got {names!r}"
        )

    def test_src_directory_exists(self, copier_defaults: dict, project_factory) -> None:
        """src directory should exist."""
        project = project_factory(copier_defaults)
        assert (project / "src").is_dir()

    def test_tests_directory_has_placeholder(self, copier_defaults: dict, project_factory) -> None:
        """tests/ ships with a placeholder so the first commit doesn't fail on pytest exit 5.

        Both `app` and `lib` project types must get the placeholder -- there's no
        conditional `_exclude`, so a missing file in either would be a regression.
        """
        for project_type in ("app", "lib"):
            project = project_factory(copier_defaults, project_type)
            tests_dir = project / "tests"
            assert tests_dir.is_dir(), f"tests/ missing for {project_type} project"
            assert (tests_dir / "__init__.py").exists(), f"tests/__init__.py missing for {project_type}"
            # python_package_import_name = "Test Project" | slugify("_") = "test_project"
            placeholder = tests_dir / "test_test_project.py"
            assert placeholder.exists(), f"placeholder test missing for {project_type}"
            content = placeholder.read_text()
            assert "import test_project" in content
            assert "def test_" in content


class TestCIConfiguration:
    """Test CI configuration options."""

    def test_ci_enabled_creates_workflow(self, copier_defaults: dict, project_factory) -> None:
        """CI enabled should create workflow file."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)
        assert (project / ".github" / "workflows" / "ci.yml").exists()

    def test_ci_disabled_no_workflow(self, copier_defaults: dict, project_factory) -> None:
        """CI disabled should not create workflow file."""
        answers = {**copier_defaults, "use_ci": False}
        project = project_factory(answers)
        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_semantic_release_creates_workflow(self, copier_defaults: dict, project_factory) -> None:
        """Semantic release enabled should create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)
        assert (project / ".github" / "workflows" / "release.yml").exists()

    def test_semantic_release_disabled_no_workflow(self, copier_defaults: dict, project_factory) -> None:
        """Semantic release disabled should not create release workflow."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": False}
        project = project_factory(answers)
        assert not (project / ".github" / "workflows" / "release.yml").exists()


class TestPythonVersion:
    """Test Python version configuration."""

    def test_requires_python_314(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should require Python 3.14+."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'requires-python = ">=3.14"' in content

    def test_ruff_target_py314(self, copier_defaults: dict, project_factory) -> None:
        """Ruff should target Python 3.14."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert 'target-version = "py314"' in content


class TestPreCommitConfig:
    """Test pre-commit configuration."""

    def test_prek_version(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should pin prek to the tested floor (>=0.4.10 provides the `[update]` tag filters)."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert 'minimum_prek_version = "0.4.12"' in content

    def test_testmon_hook_pins_coverage_core(self, copier_defaults: dict, project_factory) -> None:
        """The testmon hook must force the ctrace coverage core.

        coverage picks the sys.monitoring core by default on CPython 3.14+, and that
        core cannot do dynamic contexts. testmon calls `switch_context()` per test,
        coverage warns, `filterwarnings = ["error"]` promotes it, and pytest aborts
        with INTERNALERROR -- so the FIRST commit in a fresh project fails.

        `TestIntegration::test_first_commit_succeeds_with_prek_hooks` covers the same
        ground end-to-end, but it is marked slow. This is the fast guard.

        Scoped via prek's per-hook `env` rather than `[tool.coverage.run] core`, so
        pytest-cov keeps the faster default core. Must stay `env` and not an
        `env VAR=value` prefix on `entry`: prek execs the entry without a shell, and
        the CI matrix includes Windows.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        hooks = [h for repo in data["repos"] for h in repo.get("hooks", [])]
        testmon = next((h for h in hooks if h.get("id") == "pytest-testmon"), None)
        assert testmon is not None, "the generated prek.toml must define a pytest-testmon hook"
        assert testmon.get("env", {}).get("COVERAGE_CORE") == "ctrace", (
            "the testmon hook must set COVERAGE_CORE=ctrace, or the first commit in a "
            f"freshly scaffolded project dies with a coverage INTERNALERROR. Got {testmon.get('env')!r}"
        )
        assert not testmon["entry"].startswith("env "), (
            f"use prek's `env` key, not an `env VAR=value` entry prefix; got {testmon['entry']!r}"
        )

    def test_has_betterleaks(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should have betterleaks."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "betterleaks" in content

    def test_has_betterleaks_config(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should have a .betterleaks.toml config file."""
        project = project_factory(copier_defaults)

        config = project / ".betterleaks.toml"
        assert config.exists()
        content = config.read_text()
        assert "[[allowlists]]" in content

    def test_no_pyupgrade(self, copier_defaults: dict, project_factory) -> None:
        """Pre-commit config should not have pyupgrade (replaced by ruff UP)."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "pyupgrade" not in content

    def test_rev_lines_have_no_trailing_comment(self, copier_defaults: dict, project_factory) -> None:
        """Every `rev` line must be matchable by sync-with-uv (DOT-603).

        sync-with-uv matches revs with a regex anchored at end-of-line, so a
        trailing comment makes the line unmatchable. The hook then matches zero
        revs and reports success, silently doing nothing forever. This is the
        regex from sync_with_uv.py verbatim, so this test fails for the same
        reason the real hook would go quiet.
        """
        repo_rev_re = re.compile(r"""^\s*rev\s*=\s*(['"])([^'"]*)\1\s*$""")
        project = project_factory(copier_defaults)

        rev_lines = [line for line in (project / "prek.toml").read_text().splitlines() if re.match(r"^\s*rev\s*=", line)]
        assert rev_lines, "expected prek.toml to declare at least one rev"

        unmatched = [line for line in rev_lines if not repo_rev_re.match(line)]
        assert not unmatched, (
            "these rev lines are invisible to sync-with-uv, which would silently "
            f"stop syncing hook versions with uv.lock: {unmatched!r}. Put per-repo "
            "notes on the line above the rev, not after it."
        )

    def test_typos_hook_does_not_write_changes(self, copier_defaults: dict, project_factory) -> None:
        """The typos hook must report, not rewrite files in place (DOT-604).

        Upstream ships `args = ["--write-changes", "--force-exclude"]`. Left at
        the default it edits files, and has corrupted hex identifiers (Mongo
        ObjectIds, git SHAs) that it read as misspelled prose. Config `args`
        replace the upstream list rather than appending, so the override must
        also re-supply `--force-exclude` or _typos.toml stops being honoured
        when prek passes explicit staged filenames.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        typos = [hook for repo in data["repos"] for hook in repo.get("hooks", []) if hook["id"] == "typos"]
        assert typos, "expected a typos hook in prek.toml"

        for hook in typos:
            args = hook.get("args")
            assert args is not None, (
                "typos must override args; the upstream default includes --write-changes, which rewrites files in place."
            )
            assert "--write-changes" not in args, f"typos must not run with --write-changes; got {args!r}"
            assert "--force-exclude" in args, (
                f"keep --force-exclude so _typos.toml exclusions still apply when prek passes explicit filenames; got {args!r}"
            )

    def test_builtin_hook_ids_are_real(self, copier_defaults: dict, project_factory) -> None:
        """Every `repo = "builtin"` hook id must exist in `prek util list-builtins`.

        A typo'd or retired builtin id is not a hard error at config-parse time,
        so the hook simply never runs — the same "reports success while doing
        nothing" shape as DOT-603 and DOT-604.

        `prek` is a dev dependency specifically so this runs in CI rather than
        only on machines that happen to have it installed.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        configured = {hook["id"] for repo in data["repos"] if repo.get("repo") == "builtin" for hook in repo.get("hooks", [])}
        assert configured, "expected a builtin repo block in prek.toml"

        result = subprocess.run(["prek", "util", "list-builtins"], capture_output=True, text=True, check=True)
        available = set(result.stdout.split())

        # Guard the parse itself: this asserts a subset relation, so an output
        # format that stops being one-bare-id-per-line would make `available`
        # junk and the assertion below vacuously true rather than failing.
        assert "trailing-whitespace" in available, (
            f"could not parse `prek util list-builtins`; expected bare ids, got {result.stdout[:200]!r}"
        )

        assert configured <= available, f"not real prek builtins: {sorted(configured - available)}"

    def test_file_mutating_hooks_do_not_share_a_priority(self, copier_defaults: dict, project_factory) -> None:
        """Hooks writing the same files must not share a priority group.

        prek's reference calls two same-group hooks mutating the same files
        "undefined", and a group that modifies files fails as a whole with no
        attribution to the hook responsible. Measured at 12/40 files losing
        their trailing-whitespace fix with three such hooks sharing group 0,
        and 0/40 once each got its own.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        # Every hook that writes to the files it is handed. `typos` is absent on
        # purpose — the template drops upstream's --write-changes, so it only
        # reports (see test_typos_hook_does_not_write_changes).
        #
        # The universal ones run over every text file, so they overlap with each
        # other AND with every scoped fixer below. The scoped ones write
        # disjoint file types (.py / .md / prek.toml / uv.lock) and may safely
        # share a group with each other — except ruff and ruff-format, which
        # both rewrite .py.
        universal = {"trailing-whitespace", "end-of-file-fixer", "mixed-line-ending", "fix-byte-order-marker"}
        scoped = {"ruff", "ruff-format", "markdownlint", "sync-with-uv", "uv-lock"}

        priorities: dict[str, int] = {}
        for repo in data["repos"]:
            for hook in repo.get("hooks", []):
                if hook["id"] in universal | scoped:
                    priorities[hook["id"]] = hook.get("priority", 0)

        missing = universal - priorities.keys()
        assert not missing, f"expected these mutating hooks in prek.toml: {sorted(missing)}"

        for hook_id in universal:
            clashes = [other for other, p in priorities.items() if other != hook_id and p == priorities[hook_id]]
            assert not clashes, (
                f"{hook_id!r} rewrites every text file and shares priority {priorities[hook_id]} with {clashes}; "
                "concurrent writers lose each other's edits. Give it an unused priority."
            )

        if {"ruff", "ruff-format"} <= priorities.keys():
            assert priorities["ruff"] < priorities["ruff-format"], (
                "ruff --fix and ruff-format both rewrite .py files, so they must not share a priority, "
                "and formatting must come after fixing."
            )

        # Read-after-write, not two writers: sync-with-uv reads uv.lock to
        # update prek.toml's rev lines, and uv-lock writes uv.lock. Sharing a
        # group lets sync-with-uv read a stale lockfile and silently sync
        # nothing, which the same-file check above would not catch.
        if {"uv-lock", "sync-with-uv"} <= priorities.keys():
            assert priorities["uv-lock"] < priorities["sync-with-uv"], (
                "sync-with-uv reads the uv.lock that uv-lock writes, so uv-lock must run in an earlier priority group."
            )

    def test_no_commit_to_branch_is_not_shipped(self, copier_defaults: dict, project_factory) -> None:
        """Generated projects must not block commits to their default branch.

        `no-commit-to-branch` is a workflow opinion, not a correctness check.
        This template has users who commit straight to main by choice; shipping
        the hook would break that on the first commit with no way to discover
        why beyond reading prek.toml. Kept out on purpose — the maintainers'
        own prek.toml is where a branch policy belongs, not the template's.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        ids = [hook["id"] for repo in data["repos"] for hook in repo.get("hooks", [])]
        assert "no-commit-to-branch" not in ids, (
            "no-commit-to-branch imposes a branching workflow on every generated project; leave that to the user."
        )

    def test_has_typos_config(self, copier_defaults: dict, project_factory) -> None:
        """Generated project ships a _typos.toml excluding generated files (DOT-604).

        Release tooling writes abbreviated git SHAs into CHANGELOG.md, which
        typos reads as prose.
        """
        project = project_factory(copier_defaults)

        config = project / "_typos.toml"
        assert config.exists(), "generated project should ship a _typos.toml"

        with config.open("rb") as f:
            data = tomllib.load(f)

        excluded = data["files"]["extend-exclude"]
        assert "CHANGELOG.md" in excluded
        assert "uv.lock" in excluded
        assert ".copier-answers.yml" in excluded, (
            "copier writes `_commit: <git describe>` here, and short SHAs are hex — any of "
            "caf/beef/fade/dead/deca trips the dictionary. Without this exclusion the hook "
            "fails on a minority of commits, and `copier update` breaks if it is ever 'fixed'."
        )


class TestSemanticReleaseBuildCommand:
    """build_command must fail loudly and reach the network (DOT-602, DOT-605)."""

    @staticmethod
    def _semantic_release(project: Path) -> dict:
        with (project / "pyproject.toml").open("rb") as f:
            return tomllib.load(f)["tool"]["semantic_release"]

    def test_build_command_aborts_on_failure(self, copier_defaults: dict, project_factory) -> None:
        """build_command must `set -e` so a failing `uv lock` aborts the release (DOT-602).

        python-semantic-release runs build_command as a shell script rather
        than an `&&` chain. Without `set -e`, a failed `uv lock` lets the
        following lines run anyway, `uv build` exits 0, and the release is
        reported green having committed a stale lockfile. Nothing downstream
        catches it either: the generated CI runs `uv sync --frozen`, which
        consumes the lockfile as-is instead of asserting freshness.
        """
        project = project_factory({**copier_defaults, "use_semantic_release": True})
        build_command = self._semantic_release(project)["build_command"]

        lines = [line.strip() for line in build_command.strip().splitlines() if line.strip()]
        assert lines, "build_command should not be empty"
        assert lines[0] == "set -e", (
            "build_command must start with `set -e`, otherwise a failing `uv lock` is "
            f"swallowed and the release silently ships a stale lockfile. Got {lines!r}"
        )

    def test_build_command_env_passes_through_network_config(self, copier_defaults: dict, project_factory) -> None:
        """build_command_env must forward TLS/proxy/cache config (DOT-605).

        python-semantic-release replaces rather than extends the environment
        for build_command, keeping only a hardcoded allowlist. Since
        build_command runs `uv lock`, a network operation, anything not listed
        here is dropped and the lock runs without the CI's TLS, proxy and cache
        settings. uv 0.12 made an invalid SSL_CERT_FILE/SSL_CERT_DIR a hard
        HTTPS failure rather than a warning, so this is release-breaking on any
        project behind a corporate CA or proxy.
        """
        project = project_factory({**copier_defaults, "use_semantic_release": True})
        config = self._semantic_release(project)

        assert "build_command_env" in config, (
            "build_command runs `uv lock` over the network, so build_command_env must "
            "forward the environment python-semantic-release would otherwise drop."
        )
        env = config["build_command_env"]

        for required in ("UV_SYSTEM_CERTS", "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE"):
            assert required in env, f"{required} must be forwarded for corporate-CA setups; got {env!r}"

        # Proxy variables must travel as a set: HTTPS_PROXY without NO_PROXY
        # routes internal hosts through the corporate proxy, which is the exact
        # failure this replaces. Both cases matter -- tools disagree on which
        # they read.
        for lower in ("http_proxy", "https_proxy", "no_proxy"):
            assert lower in env, f"{lower} missing; proxy vars must be forwarded as a set. Got {env!r}"
            assert lower.upper() in env, f"{lower.upper()} missing; proxy vars must be forwarded as a set. Got {env!r}"

    def test_build_command_env_entries_are_pass_through(self, copier_defaults: dict, project_factory) -> None:
        """Entries must be bare names, not `NAME=value` literals.

        A bare entry is resolved as os.getenv(name, ""), forwarding whatever CI
        set. Hardcoding a value in the template would override the CI's real
        configuration instead of passing it through.
        """
        project = project_factory({**copier_defaults, "use_semantic_release": True})
        env = self._semantic_release(project)["build_command_env"]

        hardcoded = [entry for entry in env if "=" in entry]
        assert not hardcoded, f"build_command_env entries must be pass-through names, not literals: {hardcoded!r}"

    @staticmethod
    def _assert_uv_vars_guarded(config: dict, source: str) -> None:
        """Every forwarded UV_* variable must be unset when it arrives empty (DOT-615).

        python-semantic-release assigns bare build_command_env entries
        unconditionally via os.getenv(name, ""), so a variable that is unset in
        CI reaches the subprocess as an empty string rather than being omitted.
        uv parses its own UV_* variables as typed CLI values -- an enum for
        --link-mode, a path for --cache-dir, a boolish for --system-certs -- so
        an empty one is a malformed value rather than an absent one, and `uv
        lock` exits 2 before doing any work.

        The TLS and proxy variables are read as plain strings where empty
        already means unset, so they are exempt. Restricting the check to UV_*
        is also the invariant any future addition to the list has to satisfy.
        """
        build_command = config["build_command"]

        for name in [entry for entry in config["build_command_env"] if entry.startswith("UV_")]:
            assert f"unset {name}" in build_command, (
                f"{source}: {name} is forwarded but never unset when empty. "
                f"python-semantic-release will pass {name}='' to `uv lock`, which rejects "
                f'it as a malformed value and aborts the release. Add `[ -n "${name}" ] '
                f"|| unset {name}` to build_command. Got:\n{build_command}"
            )

    def test_forwarded_uv_variables_are_unset_when_empty(self, copier_defaults: dict, project_factory) -> None:
        """Generated projects must guard every forwarded UV_* variable (DOT-615)."""
        project = project_factory({**copier_defaults, "use_semantic_release": True})
        self._assert_uv_vars_guarded(self._semantic_release(project), "generated project")

    def test_this_repo_guards_its_own_forwarded_uv_variables(self) -> None:
        """The template's own release config needs the same guards (DOT-615).

        `[tool.semantic_release]` is one of the dual configs: it exists both in
        `project/pyproject.toml.jinja` and in this repo's `pyproject.toml`,
        which is what releases the template itself. Every other test in this
        class inspects a generated project only, so a regression confined to
        this repo's copy passes the whole suite and surfaces as a failed
        release -- which is exactly how DOT-615 was found.
        """
        with (REPO_ROOT / "pyproject.toml").open("rb") as f:
            self._assert_uv_vars_guarded(tomllib.load(f)["tool"]["semantic_release"], "this repo's pyproject.toml")


class TestHookProfiles:
    """use_heavy_hooks gates slow git hooks; fast hooks stay always-on."""

    @staticmethod
    def _hook_ids(project: Path) -> list[str]:
        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)
        return [hook["id"] for repo in data["repos"] for hook in repo.get("hooks", [])]

    def test_heavy_hooks_include_coverage(self, copier_defaults: dict, project_factory) -> None:
        """use_heavy_hooks=true runs coverage as a git hook."""
        ids = self._hook_ids(project_factory({**copier_defaults, "use_heavy_hooks": True}))
        assert "pytest-cov" in ids

    def test_light_hooks_are_the_default(self, copier_defaults: dict, project_factory) -> None:
        """The default profile (heavy hooks off) drops coverage but keeps the fast hooks."""
        ids = self._hook_ids(project_factory(copier_defaults))
        assert "pytest-cov" not in ids
        for fast in ("ruff", "ty", "pytest-testmon"):
            assert fast in ids, f"{fast} should stay always-on"

    def test_conventional_commit_gated_on_semantic_release(self, copier_defaults: dict, project_factory) -> None:
        """conventional-pre-commit ships only with semantic-release, and without --strict."""
        with_release = project_factory({**copier_defaults, "use_semantic_release": True})
        assert "conventional-pre-commit" in self._hook_ids(with_release)
        assert "--strict" not in (with_release / "prek.toml").read_text()

        without_release = project_factory(
            {
                **copier_defaults,
                "use_ci": False,
                "use_semantic_release": False,
            }
        )
        assert "conventional-pre-commit" not in self._hook_ids(without_release)


class TestDependencies:
    """Test dependency configuration."""

    def test_no_yore_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should not have yore dependency."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "yore" not in content

    def test_no_tomli_dependency(self, copier_defaults: dict, project_factory) -> None:
        """Generated project should not have tomli dependency."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tomli" not in content

    def test_prek_version_updated(self, copier_defaults: dict, project_factory) -> None:
        """prek dependency tracks the tested floor (>=0.4.10 introduced the `[update]` tag filters, DOT-616)."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert '"prek>=0.4.12"' in content

    # Floors track the versions the template is actually exercised against, not the
    # oldest release that happens to still work. `uv sync` resolves to the newest
    # release, so the bottom of a `>=8` range is a configuration nobody has ever run
    # the template under -- it advertises support that is not verified. Pinning them
    # here makes widening a range a deliberate, reviewed edit rather than a leftover.
    EXPECTED_FLOORS: ClassVar[dict[str, dict[str, str]]] = {
        "maintain": {"build": "1.5", "python-semantic-release": "10.6"},
        "ci": {
            "ruff": "0.16.1",
            "pytest": "9",
            "pytest-cov": "7",
            "pytest-randomly": "4",
            "ty": "0.0.66",
            "poethepoet": "0.48",
        },
        "local": {"prek": "0.4.12", "pytest-testmon": "2.2"},
    }

    @staticmethod
    def _floors(specs: list[str]) -> dict[str, str]:
        """Map ``["pytest>=9", ...]`` to ``{"pytest": "9", ...}``, ignoring unpinned entries."""
        return dict(spec.split(">=", 1) for spec in specs if ">=" in spec)

    def test_shipped_dependency_floors_are_current(self, copier_defaults: dict, project_factory) -> None:
        """Every tool group must declare the floor the template is tested at.

        Note these live inside the `dependency-groups` template-preserve region, so
        raising them reaches newly generated projects only. That is fine while no
        config depends on the newer behaviour -- when one does, the guard has to go
        in the propagated section instead, the way ruff's `required-version` and
        prek's `minimum_prek_version` do.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            groups = tomllib.load(f)["dependency-groups"]

        for group, expected in self.EXPECTED_FLOORS.items():
            actual = self._floors(groups[group])
            for package, floor in expected.items():
                assert actual.get(package) == floor, (
                    f"[dependency-groups] {group}: expected {package}>={floor}, got {actual.get(package)!r}"
                )

    def test_every_tool_dependency_declares_a_floor(self, copier_defaults: dict, project_factory) -> None:
        """No bare package names in the tool groups.

        An unpinned entry resolves to whatever exists on the day someone runs
        `uv sync`, which is exactly the unverified-configuration problem the floors
        exist to prevent -- except silently, since there is nothing to review.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            groups = tomllib.load(f)["dependency-groups"]

        unpinned = {group: [s for s in groups[group] if ">=" not in s] for group in self.EXPECTED_FLOORS}
        assert not any(unpinned.values()), f"tool dependencies must declare a `>=` floor: { {g: v for g, v in unpinned.items() if v} }"

    def test_this_repo_is_not_older_than_the_floors_it_ships(self, copier_defaults: dict, project_factory) -> None:
        """The template's own dev group must not lag the floors it hands to users.

        This repo and `project/pyproject.toml.jinja` are the usual dual-config pair,
        and the template half is the one that gets attention. `ty>=0.0.14` sat here
        for fifty patch releases while the template shipped a current floor -- so the
        tool the template claims to be tested against was not the one testing it.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            shipped = tomllib.load(f)["dependency-groups"]
        with (REPO_ROOT / "pyproject.toml").open("rb") as f:
            ours = self._floors(tomllib.load(f)["dependency-groups"]["dev"])

        def parts(version: str) -> tuple[int, ...]:
            return tuple(int(n) for n in version.split(".") if n.isdigit())

        for group in self.EXPECTED_FLOORS:
            for package, floor in self._floors(shipped[group]).items():
                if package in ours:
                    assert parts(ours[package]) >= parts(floor), (
                        f"this repo pins {package}>={ours[package]} but ships {package}>={floor} to generated projects"
                    )


class TestCIWorkflows:
    """Test CI workflow configuration (from smoke_test.sh assertions)."""

    def test_ci_pull_request_trigger_is_unfiltered(self, copier_defaults: dict, project_factory) -> None:
        """CI must run on PRs targeting ANY base branch, not just main (DOT-619).

        `pull_request: {branches: [main]}` looks harmless and silently disables CI
        for stacked PRs, which target their parent branch rather than main. Every
        PR in a stack but the bottom one then gets reviewed with no signal at all
        -- not a red check, no check.

        Asserting on an absent key because that is the defect: a `branches` filter
        added back here would look like tightening and read as normal in a diff.
        The `push` trigger is intentionally left alone; scoping that one to main
        is correct.
        """
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        # "on" is the YAML 1.1 boolean true, hence the quoting in the workflow;
        # PyYAML resolves the bare key back to True, so accept either.
        workflow = yaml.safe_load(ci_yml.read_text())
        triggers = workflow.get("on", workflow.get(True))

        assert "pull_request" in triggers, "CI workflow has no pull_request trigger"
        pr_trigger = triggers["pull_request"]
        assert pr_trigger is None or "branches" not in pr_trigger, (
            "pull_request must not filter on base branch -- a `branches` filter means stacked PRs "
            f"(base != main) never trigger CI. Got: {pr_trigger!r}"
        )

    def test_ci_has_setup_uv(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow should use setup-uv action."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        content = ci_yml.read_text()
        assert "astral-sh/setup-uv" in content

    def test_ci_poe_tasks_exist_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """All poe tasks referenced in CI workflow should exist in pyproject.toml."""
        import re

        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        ci_yml = project / ".github" / "workflows" / "ci.yml"
        pyproject = project / "pyproject.toml"

        ci_content = ci_yml.read_text()
        pyproject_content = pyproject.read_text()

        # Find all poe task references in CI (e.g., "uv run poe check", "uv run poe docs-build")
        poe_tasks = re.findall(r"uv run poe ([\w-]+)", ci_content)

        # Verify each task exists in pyproject.toml
        for task in poe_tasks:
            assert "[tool.poe.tasks]" in pyproject_content, "pyproject.toml should have poe tasks"
            # Check task is defined (as string, array, or dotted table like check.parallel)
            assert f"{task} = " in pyproject_content or f"{task} = [" in pyproject_content or f"{task}." in pyproject_content, (
                f"poe task '{task}' referenced in CI but not defined in pyproject.toml"
            )

    def test_release_has_semantic_release(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use semantic-release."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "semantic-release" in content

    def test_release_checks_out_main(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should checkout main explicitly (workflow_run defaults to PR branch)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "ref: main" in content

    def test_release_has_uv_publish(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow should use uv publish in separate pypi-publish job."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "uv publish" in content

    def test_release_setup_uv_has_github_token(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow setup-uv steps should have github-token to avoid rate limiting (#237)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "github-token:" in content

    def test_release_setup_uv_has_github_token_no_pypi(self, copier_defaults: dict, project_factory) -> None:
        """Release workflow release job setup-uv should have github-token even without pypi-publish job (#237)."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": False}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "github-token:" in content

    def test_ci_setup_uv_has_github_token(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow setup-uv steps should have github-token to avoid rate limiting (#237)."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "github-token:" in content

    def test_ci_has_prek_action(self, copier_defaults: dict, project_factory) -> None:
        """CI workflow should use prek-action for comprehensive quality checks."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "j178/prek-action" in content

    def test_ci_prek_skips_redundant_hooks(self, copier_defaults: dict, project_factory) -> None:
        """CI prek job should skip hooks redundant with dedicated CI jobs."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "SKIP: pytest-testmon,uv-lock" in content
        # `no-commit-to-main` was removed from the template (DOT-541) — must not reappear in SKIP.
        assert "no-commit-to-main" not in content, (
            "CI workflow still references `no-commit-to-main` in SKIP — the hook was removed "
            "from prek.toml (DOT-541), so this entry must go too."
        )

    def test_ci_prek_refreshes_lockfile(self, copier_defaults: dict, project_factory) -> None:
        """CI prek job should refresh the lockfile before running hooks."""
        answers = {**copier_defaults, "use_ci": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "ci.yml").read_text()
        assert "run: uv lock\n" in content
        lock_idx = content.index("run: uv lock")
        prek_idx = content.index("j178/prek-action")
        assert lock_idx < prek_idx

    def test_pyproject_has_build_system(self, copier_defaults: dict, project_factory) -> None:
        """pyproject.toml should have build-system section."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[build-system]" in content

    def test_uv_build_has_upper_bound(self, copier_defaults: dict, project_factory) -> None:
        """`build-system.requires` must pin `uv_build` with an upper bound (DOT-589).

        The bound is uv's own recommendation, not this template's: `uv_build`
        follows uv's versioning policy, so a minor may change build behaviour,
        and uv's docs ask for an upper bound for exactly that reason. `uv init`
        emits `uv_build>=0.12.1,<0.13.0` on uv 0.12.1; the template matches that
        shape. An unbounded spec also makes uv warn on every `uv sync` / `uv
        build`, drowning out real warnings. Bump the window when uv does.
        """
        project = project_factory(copier_defaults)

        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)

        requires = data["build-system"]["requires"]
        uv_build_specs = [r for r in requires if r.startswith(("uv_build", "uv-build"))]
        assert uv_build_specs, f"build-system.requires must list uv_build; got {requires!r}"

        spec = uv_build_specs[0]
        # Reject bare "uv_build" or specs without an upper bound. The point of
        # the pin is to keep a future breaking release from being auto-picked
        # by the build frontend — so an upper bound (`<` or `<=`) is required.
        assert "<" in spec, (
            f"uv_build must have an upper version bound to avoid the uv warning and "
            f"to prevent silent breakage on a future major release. Got {spec!r}; "
            f"expected something like 'uv_build>=0.12,<0.13'."
        )

    def test_pypi_false_excludes_classifiers_and_keywords(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, classifiers and keywords should not be in pyproject.toml."""
        answers = {**copier_defaults, "publish_to_pypi": False}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_pypi_true_includes_classifiers_and_keywords(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, classifiers and keywords should be in pyproject.toml."""
        answers = {**copier_defaults, "publish_to_pypi": True}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" in content
        assert "keywords" in content

    def test_pypi_true_has_environment(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, release workflow should have environment: pypi."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": True}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "name: pypi" in content

    def test_pypi_false_no_environment(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, release workflow should not have environment: pypi."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True, "publish_to_pypi": False}
        project = project_factory(answers)

        release_yml = project / ".github" / "workflows" / "release.yml"
        content = release_yml.read_text()
        assert "name: pypi" not in content

    def test_pypi_false_no_readme_badge(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is false, README should not have PyPI badge (#165)."""
        answers = {**copier_defaults, "publish_to_pypi": False}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pypi.org/project/" not in content

    def test_pypi_true_has_readme_badge(self, copier_defaults: dict, project_factory) -> None:
        """When publish_to_pypi is true, README should have PyPI badge."""
        answers = {**copier_defaults, "publish_to_pypi": True}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pypi.org/project/" in content


class TestCascadingBooleanDefaults:
    """Test that boolean question defaults cascade correctly when parent questions are disabled.

    Regression tests for https://github.com/detailobsessed/copier-uv-bleeding/issues/45
    When use_ci=false, downstream questions (use_semantic_release, publish_to_pypi,
    use_blacksmith_runners) should all default to false since their 'when' conditions
    prevent them from being asked.
    """

    def test_use_ci_false_no_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false (without explicit publish_to_pypi), classifiers should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        # Remove keys that should cascade from use_ci
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_use_ci_false_no_release_workflow(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, release.yml should not be created."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "release.yml").exists()
        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_use_ci_false_no_pypi_environment(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, no PyPI-related config should appear in release workflow."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        # No release workflow at all
        assert not (project / ".github" / "workflows" / "release.yml").exists()

    def test_use_ci_false_no_matrix_in_nonexistent_ci(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, CI workflow should not exist (no matrix testing)."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "ci.yml").exists()

    def test_use_ci_true_defaults_include_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=true with defaults, classifiers should appear (positive case)."""
        answers = {
            **copier_defaults,
            "use_ci": True,
        }
        # Remove to let them cascade from use_ci=true → default true
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" in content
        assert "keywords" in content

    def test_use_ci_true_defaults_create_all_workflows(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=true with defaults, both CI and release workflows should exist."""
        answers = {
            **copier_defaults,
            "use_ci": True,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert (project / ".github" / "workflows" / "ci.yml").exists()
        assert (project / ".github" / "workflows" / "release.yml").exists()

    def test_use_semantic_release_false_no_classifiers(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=false, publish_to_pypi should cascade to false."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": False,
        }
        answers.pop("publish_to_pypi", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "classifiers" not in content
        assert "keywords" not in content

    def test_use_ci_false_no_semantic_release_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_ci=false, semantic_release config and maintain group should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" not in content
        assert "python-semantic-release" not in content
        assert "maintain" not in content

    def test_use_semantic_release_false_no_semantic_release_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=false explicitly, semantic_release config should not appear."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": False,
        }
        answers.pop("publish_to_pypi", None)
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" not in content
        assert "python-semantic-release" not in content
        assert "maintain" not in content

    def test_changelog_file_under_changelog_not_default_templates(self, copier_defaults: dict, project_factory) -> None:
        """changelog_file should be under [tool.semantic_release.changelog], not default_templates (#261)."""
        answers = {**copier_defaults, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert 'changelog_file = "CHANGELOG.md"' in content
        assert "[tool.semantic_release.changelog.default_templates]" not in content

    def test_use_semantic_release_true_has_config(self, copier_defaults: dict, project_factory) -> None:
        """When use_semantic_release=true, semantic_release config and maintain group should appear."""
        answers = {
            **copier_defaults,
            "use_ci": True,
            "use_semantic_release": True,
        }
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.semantic_release]" in content
        assert "python-semantic-release" in content
        assert "maintain" in content


class TestTemplateCleanup:
    """Test removal of overly specific config and proper gating of platform-specific tasks.

    Regression tests for #49 (docs-deploy) and #50 (coverage.paths, ty.src.exclude).
    """

    def test_no_coverage_paths(self, copier_defaults: dict, project_factory) -> None:
        """Generated pyproject.toml should not have [tool.coverage.paths]."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "[tool.coverage.paths]" not in content

    def test_coverage_excludes_main_guard(self, copier_defaults: dict, project_factory) -> None:
        """Coverage exclude_lines should include if __name__ == '__main__' (#57)."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "if __name__ == .__main__." in content

    def test_description_with_quotes(self, copier_defaults: dict, project_factory) -> None:
        """Project description containing double quotes should produce valid TOML."""
        answers = {**copier_defaults, "project_description": 'Helps you "close the loop"'}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        assert data["project"]["description"] == 'Helps you "close the loop"'

    def test_no_ty_src_exclude_fixtures(self, copier_defaults: dict, project_factory) -> None:
        """Generated pyproject.toml should not have ty.src.exclude for fixtures."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "tests/fixtures" not in content


class TestTemplateUpdateCheck:
    """Test template update check hook and related tasks (#161)."""

    def test_check_template_update_script_exists(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have check-template-update.sh hook adapter."""
        project = project_factory(copier_defaults)

        script = project / "scripts" / "check-template-update.sh"
        assert script.exists()
        content = script.read_text()
        assert "copier check-update" in content

    def test_post_checkout_in_hook_types(self, copier_defaults: dict, project_factory) -> None:
        """prek.toml should install post-checkout hooks."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        with config.open("rb") as f:
            data = tomllib.load(f)
        assert "post-checkout" in data["default_install_hook_types"]

    def test_uv_sync_hook_inherits_upstream_locked(self, copier_defaults: dict, project_factory) -> None:
        """uv-sync must NOT override `args`, so it keeps upstream's `--locked` (DOT-495).

        Overriding `args` REPLACES the upstream list rather than appending to it --
        the same mechanic that drops `--write-changes` from the typos hook (DOT-604).
        So `args = []` here would silently turn `uv sync --locked` into a plain
        `uv sync` that regenerates a drifted lockfile instead of reporting it.

        That is a deliberate rejection, not an accident: a hook that self-heals
        quietly hides the drift, and "reports success while doing nothing" is the
        shape of DOT-602, DOT-603 and DOT-617. Absence of a key is invisible in a
        diff, hence this test.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        uv_repo = next(r for r in data["repos"] if r.get("repo", "").endswith("/uv-pre-commit"))
        uv_sync = next(h for h in uv_repo["hooks"] if h["id"] == "uv-sync")
        assert "args" not in uv_sync, (
            "uv-sync must inherit upstream's `args = ['--locked']`. Overriding `args` replaces "
            f"that list, so a drifted lockfile would be regenerated silently instead of failing. Got: {uv_sync!r}"
        )

    def test_check_template_update_hook_exists(self, copier_defaults: dict, project_factory) -> None:
        """prek.toml should have check-template-update hook."""
        project = project_factory(copier_defaults)

        config = project / "prek.toml"
        content = config.read_text()
        assert "check-template-update" in content

    def test_check_template_poe_task(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have check-template poe task that calls copier check-update."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "copier check-update" in content
        assert "check-template" in content

    def test_update_template_poe_task(self, copier_defaults: dict, project_factory) -> None:
        """Rendered projects should have update-template poe task that chains uv sync --upgrade and prek update."""
        project = project_factory(copier_defaults)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "update-template" in content
        assert "copier update" in content
        # update-template must pass both:
        #   --defaults    → don't prompt on newly-added questions; use their defaults.
        #                   Required so the task survives non-TTY contexts (CI, scripted
        #                   runs, agent sessions); otherwise copier crashes inside
        #                   questionary trying to open a prompt. DOT-542 originally banned
        #                   this flag under the wrong premise that it caused pyproject.toml
        #                   clobbering — verified: clobbering is driven by copier's 3-way
        #                   merge engine, not by --defaults, which only governs questions.
        #   --conflict rej → separate .rej files instead of inline conflict markers in
        #                    working files, so the user sees what copier couldn't apply.
        assert "--defaults" in content
        assert "--conflict rej" in content
        assert "uv sync --upgrade" in content
        assert "prek update" in content
        assert not (project / "scripts" / "prek-autoupdate.sh").exists(), (
            "the wrapper script was replaced by a declarative `[update.repos]` filter in prek.toml (DOT-616)"
        )

    def test_lychee_rev_is_pinned_not_empty(self, copier_defaults: dict, project_factory) -> None:
        """Lychee should have a pinned rev (not empty) since its 'nightly' tag is mutable."""
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)
        lychee_repos = [r for r in data["repos"] if r.get("repo", "").endswith("/lychee")]
        assert len(lychee_repos) == 1, "Expected exactly one lychee repo entry"
        rev = lychee_repos[0]["rev"]
        assert rev, "Lychee rev should be pinned, not empty"
        assert rev.startswith("lychee-v"), f"Lychee rev should be a versioned tag, got: {rev}"

    def test_lychee_nightly_excluded_declaratively(self, copier_defaults: dict, project_factory) -> None:
        """prek.toml must exclude lychee's `nightly` tag from `prek update` (DOT-492, DOT-540, DOT-616).

        lychee tags `nightly` as their GitHub "Latest" release, so `prek update`
        resolves it as the newest tag and rewrites the pinned rev to a mutable
        one that lychee's own hook then rejects (lycheeverse/lychee#1601).

        This lives in the config rather than in a wrapper script so that every
        invocation is covered -- a bare `prek update`, CI, an editor
        integration -- not only the one that remembers to go through the
        wrapper. Requires prek 0.4.10+, which `minimum_prek_version` enforces.
        Remove once lycheeverse/lychee#1601 is fixed upstream (DOT-504).
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        repo = "https://github.com/lycheeverse/lychee"
        filters = data.get("update", {}).get("repos", {}).get(repo)
        assert filters is not None, (
            f'prek.toml must declare [update.repos."{repo}"]; without it a plain `prek update` '
            f"rewrites the pinned rev to `nightly`. Got update config: {data.get('update')!r}"
        )
        assert "nightly" in filters.get("exclude_tags", []), f"`nightly` must be in exclude_tags for {repo}; got {filters!r}"

        assert data["minimum_prek_version"] == "0.4.12", (
            "the [update] tag filters above need prek 0.4.10+, and the floor tracks the tested version. minimum_prek_version is the guard "
            "that reaches updating projects, since the pyproject `prek>=` floor sits inside a "
            f"template-preserve region. Got {data.get('minimum_prek_version')!r}"
        )

    def test_check_merge_conflict_has_assume_in_merge(self, copier_defaults: dict, project_factory) -> None:
        """check-merge-conflict must pass --assume-in-merge so it catches markers from `copier update --conflict inline` (DOT-542).

        Without --assume-in-merge, pre-commit-hooks' check-merge-conflict only fires when git
        records a pending merge (.git/MERGE_MSG). `copier update` doesn't set that state, so the
        default-args form silently misses inline conflict markers produced by Copier.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        builtin = next(r for r in data["repos"] if r.get("repo") == "builtin")
        hook = next(h for h in builtin["hooks"] if h["id"] == "check-merge-conflict")
        assert hook.get("args") == ["--assume-in-merge"], (
            f"check-merge-conflict must pass --assume-in-merge for copier update conflicts; got {hook.get('args')!r}"
        )

    def test_no_copier_rej_files_hook(self, copier_defaults: dict, project_factory) -> None:
        """A local prek hook must block commits containing copier update .rej files (DOT-542).

        Since `update-template` now uses `--conflict rej`, an unresolved conflict produces a
        `<file>.rej` artifact. Committing those would leave the project half-merged. This hook
        enforces manual review by failing on any staged path matching `\\.rej$`.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        local_repos = [r for r in data["repos"] if r.get("repo") == "local"]
        hooks = [h for repo in local_repos for h in repo.get("hooks", [])]
        rej_hook = next((h for h in hooks if h["id"] == "no-copier-rej-files"), None)
        assert rej_hook is not None, "Expected a local 'no-copier-rej-files' hook in prek.toml"
        assert rej_hook["language"] == "fail", "Hook must use language='fail' so any matching file fails the run"
        assert rej_hook["files"] == r"\.rej$", f"Hook must target .rej files; got {rej_hook['files']!r}"

    def test_uv_sync_task_runs_in_copier_temp_render_dirs(self) -> None:
        """`uv sync --upgrade` must run in copier's temp render dirs, skip destination on update.

        Regression guard for DOT-587 (deleted uv.lock) and DOT-588 (broken .venv).

        Background: on `copier update`, copier renders OLD and NEW template versions into temp
        dirs (`copier._main.old_copy.*` / `copier._main.new_copy.*`), then deletes from the
        destination anything present in old_copy but absent in new_copy (`_remove_old_files`).

        Old template versions (≤0.34.3) ran an unguarded `uv sync` in `_tasks`, so old_copy
        ends up with `uv.lock` and a full `.venv/` tree. If NEW's task skips uv sync in
        new_copy (via a naive `[ -d .git ]` guard — temp dirs have no .git), copier sees those
        entries as "removed" and wipes the user's real `uv.lock` and `.venv`.

        The fix is the inverted guard: run in temp dirs and on `copy`, skip in destination
        during update (`poe update-template` handles destination explicitly). This test pins
        the guard so it cannot regress back to `[ -d .git ]` without an explicit decision.
        """
        copier_yml = pathlib.Path(__file__).resolve().parent.parent / "copier.yml"
        content = copier_yml.read_text()

        # The uv sync task must use the inverted guard: skip destination, run in temp dirs.
        assert "[ ! -d .git ]; then uv sync --upgrade" in content, (
            "copier.yml _tasks must run `uv sync --upgrade` in copier's temp render dirs "
            "(no .git) AND on `copy`, but skip the destination during update. "
            "Reverting to `[ -d .git ]` would re-introduce DOT-587 (deleted uv.lock) and "
            "DOT-588 (broken .venv)."
        )

        # The opposite — `[ -d .git ]; then uv sync` — must NOT be present. (Substring match
        # is intentional; rules out the naive guard even if other text wraps it.)
        assert "[ -d .git ]; then uv sync --upgrade" not in content, (
            "copier.yml _tasks has `[ -d .git ]; then uv sync --upgrade` — the naive guard "
            "that lets copier delete the user's uv.lock and .venv on update. Use "
            "`[ ! -d .git ]` instead (see DOT-587 / DOT-588)."
        )

    def test_tasks_do_not_chmod_downstream_scripts(self) -> None:
        """`_tasks` must not blanket-chmod `scripts/` (DOT-628).

        The template owns exactly one file under `scripts/`. A downstream project keeps its
        own one-off scripts in the same directory, and the template has no business changing
        their modes. `chmod +x scripts/*.sh scripts/*.py` did exactly that: every shebang-less
        `.py` a project kept there went 644 -> 755 on update, and ruff's `EXE002` turned a
        lint-clean repo red with no `.rej` file to explain it.

        Nothing replaces the task, because nothing needs to: copier chmods each rendered file
        to the template's git-index mode itself (`_render_file`), on copy and update alike.
        See `test_shipped_script_is_rendered_executable` for the other half of this pair.
        """
        copier_yml = pathlib.Path(__file__).resolve().parent.parent / "copier.yml"
        tasks = yaml.safe_load(copier_yml.read_text())["_tasks"]

        # Parse the YAML rather than grepping lines. A copier task is either a bare command
        # string or a mapping with `command` (plus `when`), and either form can put the
        # command on a folded continuation line — `- command: >-` with the body indented
        # underneath. A line-oriented filter sees no `chmod` on the `- ` line and passes
        # while copier happily runs the task.
        commands = [task if isinstance(task, str) else task.get("command", "") for task in tasks]
        offenders = [command for command in commands if "chmod" in command]

        assert not offenders, (
            "copier.yml _tasks contains a chmod task:\n"
            + "\n".join(offenders)
            + "\n\nThe template must not change modes of files it does not own — a glob over "
            "`scripts/` catches the downstream project's own scripts and breaks ruff EXE002 "
            "(DOT-628). Copier already propagates the template's exec bits; if a newly "
            "shipped script needs +x, commit it 100755 instead."
        )

    def test_shipped_script_is_rendered_executable(self, copier_defaults: dict, project_factory) -> None:
        """The one script the template ships must arrive executable, with no chmod task.

        This is the load-bearing half of DOT-628's fix: dropping the chmod task is only safe
        because copier propagates the template's own mode. If `check-template-update.sh` were
        ever committed 100644, the generated project's `check-shebang-scripts-are-executable`
        hook would fail on the very first commit — so pin the rendered mode, not the source's.
        """
        project = project_factory(copier_defaults)

        script = project / "scripts" / "check-template-update.sh"
        assert script.stat().st_mode & 0o111, (
            f"{script.name} rendered non-executable ({stat.filemode(script.stat().st_mode)}). "
            "It has a shebang, so the generated project's `check-shebang-scripts-are-executable` "
            "hook will block every commit. Commit `project/scripts/check-template-update.sh` "
            "with mode 100755 (`git update-index --chmod=+x`) — do not add a chmod task, which "
            "would re-introduce DOT-628."
        )

    def test_update_banner_does_not_claim_deps_synced(self) -> None:
        """The `🎉 Template updated!` banner must not claim "Dependencies synced" (DOT-587 fix follow-up).

        With the inverted `uv sync` guard (see test_uv_sync_task_runs_in_copier_temp_render_dirs),
        copier's _tasks no longer run uv sync in the destination during update. The poe
        `update-template` chain runs `uv sync --upgrade` after copier returns. So the banner
        — which fires from copier's _tasks before the poe chain finishes — would be lying
        if it claimed deps were already synced.
        """
        copier_yml = pathlib.Path(__file__).resolve().parent.parent / "copier.yml"
        # Pull just the line(s) containing the update banner's printf, so this only
        # inspects the user-visible string and isn't tripped by explanatory comments.
        banner_lines = [line for line in copier_yml.read_text().splitlines() if "🎉 Template updated!" in line]
        assert banner_lines, "Update banner missing from copier.yml"
        banner = "\n".join(banner_lines)

        assert "Dependencies synced" not in banner, (
            f"Update banner claims `Dependencies synced` — but copier's _tasks skip "
            f"`uv sync` in the destination during update (see DOT-587). The poe "
            f"`update-template` chain syncs deps AFTER this banner. Drop the line.\n"
            f"Banner:\n{banner}"
        )

    def test_no_commit_to_main_hook_absent(self, copier_defaults: dict, project_factory) -> None:
        """The `no-commit-to-main` pre-push hook must not ship in prek.toml (DOT-541).

        Solo workflows commit straight to main for trivial / safe changes (typo fixes, doc
        tweaks, dep bumps). The template used to ship a `no-commit-to-main` pre-push hook
        that blocked that workflow unconditionally, forcing every change through a PR even
        when there was no reviewer to wait for. The template no longer ships it; users who
        want PR-only enforcement can add a six-line local hook themselves.
        """
        project = project_factory(copier_defaults)

        with (project / "prek.toml").open("rb") as f:
            data = tomllib.load(f)

        all_hook_ids = [h["id"] for repo in data["repos"] for h in repo.get("hooks", [])]
        assert "no-commit-to-main" not in all_hook_ids, (
            f"prek.toml ships a `no-commit-to-main` hook — the template was changed to drop it "
            f"(DOT-541) so solo workflows can commit straight to main. Current hooks: {all_hook_ids!r}"
        )


class TestTemplateUpdateNotification:
    """Test the post-checkout hook adapter (check-template-update.sh) behavior."""

    SCRIPT_SRC = pathlib.Path(__file__).resolve().parent.parent / "project" / "scripts" / "check-template-update.sh"

    @classmethod
    def _setup(cls, tmp_path: Path) -> Path:
        """Create a minimal directory with the script."""
        project = tmp_path / "project"
        scripts = project / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy2(cls.SCRIPT_SRC, scripts / "check-template-update.sh")
        return project

    @staticmethod
    def _run(project: Path, *, args: list[str] | None = None) -> subprocess.CompletedProcess:
        """Run check-template-update.sh."""
        script = project / "scripts" / "check-template-update.sh"
        cmd = ["bash", str(script), *(args or [])]
        return subprocess.run(cmd, cwd=project, capture_output=True, text=True, check=False, start_new_session=True)

    def test_file_level_restore_skipped(self, tmp_path: Path) -> None:
        """Script exits silently when git signals file-level restore (arg3=0)."""
        project = self._setup(tmp_path)
        result = self._run(project, args=["oldref", "newref", "0"])
        assert result.returncode == 0
        assert not result.stdout
        assert not result.stderr


class TestGitLabSupport:
    """Test GitLab repository provider support.

    Regression tests for #51 (GitHub-specific files) and #52 (GitLab support).
    """

    def test_gitlab_no_github_directory(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have .github/ directory."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        assert not (project / ".github").exists()

    def test_gitlab_has_gitlab_ci(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects with CI should have .gitlab-ci.yml."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com", "use_ci": True}
        project = project_factory(answers)

        assert (project / ".gitlab-ci.yml").exists()
        content = (project / ".gitlab-ci.yml").read_text()
        assert "quality" in content
        assert "test" in content

    def test_gitlab_no_ci_no_gitlab_ci(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects without CI should not have .gitlab-ci.yml."""
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "use_ci": False,
        }
        answers.pop("use_semantic_release", None)
        answers.pop("publish_to_pypi", None)
        answers.pop("use_blacksmith_runners", None)
        project = project_factory(answers)

        assert not (project / ".gitlab-ci.yml").exists()
        assert not (project / ".github").exists()

    def test_gitlab_no_actionlint_in_precommit(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have actionlint pre-commit hook."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        config = project / "prek.toml"
        content = config.read_text()
        assert "actionlint" not in content

    def test_gitlab_precommit_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """GitLab prek.toml should be valid TOML with expected repos."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        config = project / "prek.toml"
        with config.open("rb") as f:
            data = tomllib.load(f)
        repo_urls = [r["repo"] for r in data["repos"]]
        assert "https://github.com/crate-ci/typos" in repo_urls

    def test_gitlab_no_discussions_url(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should not have Discussions URL."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "Discussions" not in content

    def test_gitlab_has_pipeline_badge(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have pipeline badge in README."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        readme = project / "README.md"
        content = readme.read_text()
        assert "pipeline" in content
        assert "gitlab.com" in content

    def test_gitlab_has_gitlab_urls(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have gitlab.com URLs in pyproject.toml."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com"}
        project = project_factory(answers)

        pyproject = project / "pyproject.toml"
        content = pyproject.read_text()
        assert "gitlab.com" in content

    def test_gitlab_semantic_release_remote(self, copier_defaults: dict, project_factory) -> None:
        """GitLab projects should have [tool.semantic_release.remote] with type=gitlab (#236)."""
        answers = {**copier_defaults, "repository_provider": "gitlab.com", "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" in content
        assert 'type = "gitlab"' in content
        assert "domain" not in content

    def test_gitlab_selfhosted_semantic_release_remote_domain(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should include domain in semantic_release.remote (#236)."""
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
            "use_ci": True,
            "use_semantic_release": True,
        }
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" in content
        assert 'type = "gitlab"' in content
        assert 'domain = "gitlab.company.com"' in content

    def test_github_no_semantic_release_remote(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should NOT have [tool.semantic_release.remote] section."""
        answers = {**copier_defaults, "use_ci": True, "use_semantic_release": True}
        project = project_factory(answers)

        content = (project / "pyproject.toml").read_text()
        assert "[tool.semantic_release.remote]" not in content

    def test_github_still_has_github_directory(self, copier_defaults: dict, project_factory) -> None:
        """GitHub projects should still have .github/ directory (positive case)."""
        project = project_factory(copier_defaults)

        assert (project / ".github").exists()
        assert not (project / ".gitlab-ci.yml").exists()


class TestCLIFramework:
    """Test app project type scaffolding."""

    def test_app_type_no_scaffold_code(self, copier_defaults: dict, project_factory) -> None:
        """App type should not generate scaffold source files (users create their own via uv init).

        Note: ``tests/__init__.py`` and ``tests/test_<package>.py`` ARE generated as
        a placeholder so the first commit doesn't fail the pytest-testmon hook.
        See test_tests_directory_has_placeholder.
        """
        project = project_factory(copier_defaults, "app")
        assert not (project / "src" / "test_project" / "_internal").exists()
        assert not (project / "src" / "test_project" / "__main__.py").exists()
        assert not (project / "src" / "test_project" / "py.typed").exists()
        assert not (project / "tests" / "test_cli.py").exists()
        assert not (project / "tests" / "test_api.py").exists()
        assert not (project / "tests" / "conftest.py").exists()


class TestOpenSource:
    """``open_source`` gates LICENSE + community-health files.

    When ``open_source`` is false (internal/private), the LICENSE, community-health
    files (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, issue/PR templates, FUNDING) and
    the license/Funding metadata in ``pyproject.toml`` are all omitted.
    """

    COMMUNITY_FILES: ClassVar[list[str]] = [
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        ".github/FUNDING.yml",
        ".github/pull_request_template.md",
    ]

    def test_open_source_has_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects ship all community-health files and a LICENSE."""
        project = project_factory({**copier_defaults, "open_source": True})
        for f in self.COMMUNITY_FILES:
            assert (project / f).exists(), f"{f} should exist for open-source projects"
        assert (project / ".github" / "ISSUE_TEMPLATE").exists()

    def test_internal_no_community_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects ship none of the community-health files or LICENSE."""
        project = project_factory({**copier_defaults, "open_source": False})
        for f in self.COMMUNITY_FILES:
            assert not (project / f).exists(), f"{f} should NOT exist for internal projects"
        assert not (project / ".github" / "ISSUE_TEMPLATE").exists()

    # -- pyproject.toml license + funding metadata --

    def test_internal_no_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have license metadata in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / "pyproject.toml").read_text()
        assert "license = " not in content
        assert "license-files" not in content

    def test_open_source_has_license_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects should have license metadata in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / "pyproject.toml").read_text()
        assert 'license = "MIT"' in content
        assert "license-files" in content

    def test_internal_no_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should not have a Funding URL in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / "pyproject.toml").read_text()
        assert "Funding" not in content
        assert "sponsors" not in content

    def test_open_source_has_funding_url_in_pyproject(self, copier_defaults: dict, project_factory) -> None:
        """Open-source GitHub projects should have a Funding URL in pyproject.toml."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / "pyproject.toml").read_text()
        assert "Funding" in content

    # -- Core files always present --

    def test_internal_still_has_core_files(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects should still have core project files."""
        project = project_factory({**copier_defaults, "open_source": False})
        assert (project / "pyproject.toml").exists()
        assert (project / "README.md").exists()
        assert (project / "CHANGELOG.md").exists()
        assert (project / "prek.toml").exists()
        assert (project / ".editorconfig").exists()
        assert (project / "src").is_dir()

    def test_internal_pyproject_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects pyproject.toml should be valid TOML."""
        project = project_factory({**copier_defaults, "open_source": False})
        with (project / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "project" in data

    # -- Lychee config --

    def test_internal_lychee_accepts_401(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should accept 401 for auth-gated URLs."""
        project = project_factory({**copier_defaults, "open_source": False})
        content = (project / ".lychee.toml").read_text()
        assert "401" in content

    def test_open_source_lychee_no_401(self, copier_defaults: dict, project_factory) -> None:
        """Open-source projects .lychee.toml should not accept 401."""
        project = project_factory({**copier_defaults, "open_source": True})
        content = (project / ".lychee.toml").read_text()
        assert "401" not in content

    def test_internal_lychee_valid_toml(self, copier_defaults: dict, project_factory) -> None:
        """Internal projects .lychee.toml should be valid TOML."""
        project = project_factory({**copier_defaults, "open_source": False})
        with (project / ".lychee.toml").open("rb") as f:
            data = tomllib.load(f)
        assert "accept" in data

    # -- Self-hosted repository URLs --

    def test_selfhosted_pyproject_urls(self, copier_defaults: dict, project_factory) -> None:
        """Self-hosted GitLab should use repository_host for URLs."""
        answers = {
            **copier_defaults,
            "open_source": False,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.company.com",
        }
        project = project_factory(answers)
        content = (project / "pyproject.toml").read_text()
        assert "gitlab.company.com" in content
        assert "://gitlab.com/" not in content


class TestOpenSourceMigration:
    """The 0.41.0 `_migrations` step derives `open_source` from the legacy
    `project_visibility` / `project_audience` answers.

    Without this migration, `copier update --defaults` resolves `open_source`
    from its own schema default (`repository_provider == 'github.com'`) instead
    of the project's real history, silently flipping visibility for any project
    whose history disagrees with that default — e.g. an internal project hosted
    on GitHub gains a LICENSE and community-health files with no `.rej` warning.

    A full `copier update` end-to-end run can't exercise this migration in this
    test suite: `_migrations` are gated by PEP 440 version comparison against the
    *tagged* template version, and an unreleased commit always resolves to a dev
    version below the next tag (verified manually against a temporary local
    `0.41.0` tag during development). So this tests the migration script directly.
    """

    SCRIPT: ClassVar[pathlib.Path] = REPO_ROOT / "migrations" / "0.41.0_open_source.py"

    def test_migration_registered_in_copier_yml(self) -> None:
        """copier.yml's `_migrations` entry must reference the script that actually exists."""
        content = (REPO_ROOT / "copier.yml").read_text()
        assert "migrations/0.41.0_open_source.py" in content
        assert self.SCRIPT.is_file(), f"{self.SCRIPT} referenced in copier.yml but missing"

    def _run(self, tmp_path: pathlib.Path, answers_body: str) -> str:
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(answers_body)
        result = subprocess.run(
            ["python3", str(self.SCRIPT)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"migration script failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        return answers_file.read_text()

    def test_derives_open_source_true_from_public_visibility(self, tmp_path: Path) -> None:
        """An internal-on-paper GitHub project isn't affected, but a public project must stay public."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nproject_visibility: public\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_derives_open_source_false_from_internal_visibility(self, tmp_path: Path) -> None:
        """The exact regression this migration exists for: an internal GitHub project must not
        silently become open-source (schema default is `repository_provider == 'github.com'`)."""
        result = self._run(tmp_path, "repository_provider: github.com\nproject_visibility: internal\n")
        assert re.search(r"^open_source:\s*false\s*$", result, re.MULTILINE), result

    def test_falls_back_to_project_audience_when_visibility_absent(self, tmp_path: Path) -> None:
        """Very old projects (pre-project_visibility) only have project_audience recorded."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nproject_audience: public-oss\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_leaves_existing_open_source_answer_untouched(self, tmp_path: Path) -> None:
        """If `open_source` is already answered, the migration must not override it."""
        result = self._run(tmp_path, "project_visibility: public\nopen_source: false\n")
        assert re.search(r"^open_source:\s*false\s*$", result, re.MULTILINE), result

    def test_noop_without_any_legacy_answer(self, tmp_path: Path) -> None:
        """No legacy keys to derive from — leave the file alone and let the question's own default apply."""
        original = "repository_provider: gitlab.com\n"
        result = self._run(tmp_path, original)
        assert result == original

    def test_falls_back_to_community_health_files_when_visibility_and_audience_absent(self, tmp_path: Path) -> None:
        """Projects from before project_visibility existed only have use_community_health_files."""
        result = self._run(tmp_path, "repository_provider: gitlab.com\nuse_community_health_files: true\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_derives_open_source_when_visibility_and_community_health_agree(self, tmp_path: Path) -> None:
        """The common case: use_community_health_files matches its project_visibility-derived default."""
        result = self._run(tmp_path, "project_visibility: public\nuse_community_health_files: true\n")
        assert re.search(r"^open_source:\s*true\s*$", result, re.MULTILINE), result

    def test_abstains_when_visibility_and_community_health_disagree(self, tmp_path: Path) -> None:
        """A public project with community files explicitly turned off (DOT-599 review finding):
        no single boolean preserves both axes, so the migration must not guess."""
        original = "project_visibility: public\nuse_community_health_files: false\n"
        result = self._run(tmp_path, original)
        assert result == original
        assert "open_source" not in result


class TestRemovePrekAutoupdateScriptMigration:
    """The 0.41.4 `_migrations` step deletes the orphaned `scripts/prek-autoupdate.sh`.

    `copier update` never deletes files, so without this the wrapper lingers in
    every existing project, unreferenced by `poe update-template` or the docs
    (DOT-616).

    Deleting a user's file is the risk here, so the guard is an exact digest of
    every version the template shipped rather than a substring match. A substring
    guard fails in both directions, which is a #336 review finding: it deletes a
    genuinely edited script as long as the matched line survives, and it flags the
    pre-0.40.0 script -- which used a `--cooldown-days 7` second pass and contains
    no `--repo-exclude-tag` at all -- as customised when it is pristine.
    """

    SCRIPT: ClassVar[pathlib.Path] = REPO_ROOT / "migrations" / "0.41.4_remove_prek_autoupdate_script.py"
    TARGET: ClassVar[pathlib.Path] = pathlib.Path("scripts") / "prek-autoupdate.sh"

    # Byte-for-byte as shipped. Kept here rather than read from git history so the
    # test fails if someone edits the digests in the migration to match a new file.
    SHIPPED_0_38_1: ClassVar[str] = (
        "#!/usr/bin/env bash\n"
        "# Wraps `uv run prek autoupdate` with a workaround for lychee marking `nightly` as\n"
        '# their GitHub "Latest" release (DOT-492). The second pass with --cooldown-days 7\n'
        "# reverts lychee's `rev` from `nightly` back to the most recent versioned tag.\n"
        "# Remove once lychee stops marking nightly as Latest (DOT-504).\n"
        "set -eu\n"
        'uv run prek autoupdate "$@"\n'
        'uv run prek autoupdate --repo https://github.com/lycheeverse/lychee --cooldown-days 7 "$@"\n'
    )
    SHIPPED_0_40_0: ClassVar[str] = (
        "#!/usr/bin/env bash\n"
        "# Wraps `uv run prek autoupdate` with a workaround for lychee tagging `nightly`\n"
        '# as their GitHub "Latest" release (lycheeverse/lychee#1601). The\n'
        "# --repo-exclude-tag flag (prek 0.3.11+) keeps lychee on its real latest\n"
        "# versioned tag instead of flipping to `nightly`. Remove the flag when upstream\n"
        "# closes lycheeverse/lychee#1601 (DOT-504).\n"
        "set -eu\n"
        'uv run prek autoupdate --repo-exclude-tag https://github.com/lycheeverse/lychee=nightly "$@"\n'
    )

    def test_migration_registered_in_copier_yml(self) -> None:
        """copier.yml's `_migrations` entry must reference the script that actually exists."""
        content = (REPO_ROOT / "copier.yml").read_text()
        assert "migrations/0.41.4_remove_prek_autoupdate_script.py" in content
        assert self.SCRIPT.is_file(), f"{self.SCRIPT} referenced in copier.yml but missing"

    def test_migration_commands_quote_the_script_path(self) -> None:
        """copier runs string `_migrations` commands with `shell=True`.

        `_copier_conf.src_path` is whatever the user passed to `copier copy`, so an
        unquoted path containing a space splits into two arguments and python3 fails
        to open the script (#336 review finding).
        """
        content = (REPO_ROOT / "copier.yml").read_text()
        unquoted = re.findall(r"^\s*command:\s*python3\s+(?!\")\S*\{\{.*$", content, re.MULTILINE)
        assert not unquoted, f"migration script paths must be quoted for paths with spaces: {unquoted}"

    def _run(self, tmp_path: pathlib.Path, body: str | None) -> tuple[bool, str]:
        """Run the migration in `tmp_path`; return (file still exists, stdout)."""
        target = tmp_path / self.TARGET
        target.parent.mkdir(parents=True, exist_ok=True)
        if body is not None:
            target.write_text(body, newline="")
        result = subprocess.run(["python3", str(self.SCRIPT)], cwd=tmp_path, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"migration failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        return target.exists(), result.stdout

    @pytest.mark.parametrize("shipped", ["SHIPPED_0_38_1", "SHIPPED_0_40_0"])
    def test_removes_every_version_the_template_shipped(self, tmp_path: Path, shipped: str) -> None:
        """Both shipped versions are pristine and must go, including the pre-0.40.0 one
        that predates `--repo-exclude-tag` entirely."""
        exists, stdout = self._run(tmp_path, getattr(self, shipped))
        assert not exists, f"pristine {shipped} was left behind: {stdout}"
        assert "Removed" in stdout

    def test_removes_a_shipped_version_checked_out_with_crlf(self, tmp_path: Path) -> None:
        """A Windows checkout with `core.autocrlf=true` stores the same bytes with CRLF.
        That is not a customisation and must not read as one."""
        exists, _ = self._run(tmp_path, self.SHIPPED_0_40_0.replace("\n", "\r\n"))
        assert not exists, "CRLF line endings were mistaken for a user customisation"

    def test_keeps_a_customised_script(self, tmp_path: Path) -> None:
        """The failure mode that matters: never delete work the user did.

        This script keeps the original invocation intact and only appends a line,
        which is exactly what a substring guard would wave through.
        """
        exists, stdout = self._run(tmp_path, self.SHIPPED_0_40_0 + "uv run prek run --all-files\n")
        assert exists, "a customised script was deleted"
        assert "leaving it in place" in stdout

    def test_noop_when_the_script_is_absent(self, tmp_path: Path) -> None:
        """Projects generated after 0.41.4 never had the file; the migration must stay silent."""
        exists, stdout = self._run(tmp_path, None)
        assert not exists
        assert stdout.strip() == "", f"expected no output, got: {stdout!r}"

    def test_digests_match_the_versions_actually_shipped(self) -> None:
        """Guards against the digests drifting from the file contents they claim to describe."""
        import hashlib

        content = self.SCRIPT.read_text()
        for shipped in (self.SHIPPED_0_38_1, self.SHIPPED_0_40_0):
            digest = hashlib.sha256(shipped.encode()).hexdigest()
            assert digest in content, f"migration is missing the digest for a shipped version: {digest}"


class TestMarkedSectionsSync:
    """`_tasks` step (see copier.yml) that replaces `copier update`'s fuzzy-patch
    handling of `pyproject.toml`/`prek.toml` with a regenerate-and-preserve
    approach (DOT-599): the whole file is rendered fresh from the template on
    every update, except for regions wrapped in
    `# template-preserve:&lt;name&gt;:start`/`:end` comments in the .jinja source,
    which are copied verbatim from the previous version.

    Both files moved to `_skip_if_exists`, so this script is the *only* thing
    that updates them after first generation.
    """

    SCRIPT: ClassVar[pathlib.Path] = REPO_ROOT / "migrations" / "sync_marked_sections.py"

    @staticmethod
    def _load_module():
        import importlib.util

        spec = importlib.util.spec_from_file_location("sync_marked_sections", TestMarkedSectionsSync.SCRIPT)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_script_referenced_in_copier_yml(self) -> None:
        content = (REPO_ROOT / "copier.yml").read_text()
        assert "migrations/sync_marked_sections.py" in content
        assert self.SCRIPT.is_file(), f"{self.SCRIPT} referenced in copier.yml but missing"

    def test_pyproject_and_prek_toml_in_skip_if_exists(self) -> None:
        """The whole mechanism depends on Copier's default patch-based update
        never touching these files — otherwise both it and this script would
        race to write them."""
        content = (REPO_ROOT / "copier.yml").read_text()
        skip_block = content.split("_skip_if_exists:")[1].split("_exclude:")[0]
        assert "pyproject.toml" in skip_block
        assert "prek.toml" in skip_block

    def test_unmarked_content_always_reflects_fresh_render(self) -> None:
        module = self._load_module()
        existing = "line-length = 100\n"
        new = "line-length = 140\n"
        assert module.sync_text(existing, new) == new

    def test_marked_region_preserved_verbatim(self) -> None:
        module = self._load_module()
        existing = 'a\n# template-preserve:deps:start\ndependencies = ["requests>=2"]\n# template-preserve:deps:end\nb\n'
        new = "a2\n# template-preserve:deps:start\ndependencies = []\n# template-preserve:deps:end\nb2\n"
        merged = module.sync_text(existing, new)
        assert 'dependencies = ["requests>=2"]' in merged
        assert "a2" in merged
        assert "b2" in merged

    def test_reordered_markers_match_by_name_not_position(self) -> None:
        """The bug found in Templator's own implementation (positional
        matching): a release that reorders marked regions must not splice
        content into the wrong slot."""
        module = self._load_module()
        existing = (
            "# template-preserve:foo:start\nFOO-OLD\n# template-preserve:foo:end\n"
            "# template-preserve:bar:start\nBAR-OLD\n# template-preserve:bar:end\n"
        )
        new = (
            "# template-preserve:bar:start\nBAR-DEFAULT\n# template-preserve:bar:end\n"
            "# template-preserve:foo:start\nFOO-DEFAULT\n# template-preserve:foo:end\n"
        )
        merged = module.sync_text(existing, new)
        assert "FOO-OLD" in merged
        assert "BAR-OLD" in merged
        foo_pos = merged.index("FOO-OLD")
        bar_pos = merged.index("BAR-OLD")
        assert bar_pos < foo_pos  # bar block comes first in `new`, and must keep its own content

    def test_never_seen_marker_keeps_fresh_default_instead_of_emptying(self) -> None:
        """The footgun found in Templator's own implementation: a marked
        region with no snapshot (new to this release, or never customized)
        must keep the fresh render's own default, not go blank."""
        module = self._load_module()
        existing = "x\n"  # no markers at all yet
        new = "# template-preserve:newthing:start\nDEFAULT-CONTENT\n# template-preserve:newthing:end\n"
        merged = module.sync_text(existing, new)
        assert "DEFAULT-CONTENT" in merged

    def test_markers_present_in_pyproject_template(self) -> None:
        content = (REPO_ROOT / "project" / "pyproject.toml.jinja").read_text()
        for name in ("dependencies", "project-scripts", "dependency-groups", "tool-uv-index", "extra-poe-tasks"):
            assert f"# template-preserve:{name}:start" in content, f"missing marker: {name}"
            assert f"# template-preserve:{name}:end" in content, f"missing marker: {name}"

    # --- Externally-owned scalars (DOT-620) ------------------------------

    def test_released_version_survives_update(self) -> None:
        """`project.version` is owned by semantic-release, not the template.
        The fresh render always carries the seed `0.0.0`; without preservation
        the update silently rolls a released project back to it, and
        `allow_zero_version = true` means semantic-release then *accepts*
        `0.0.0` and computes 0.1.0 instead of the real next version."""
        module = self._load_module()
        existing = '[project]\nname = "x"\nversion = "0.18.0"\n'
        new = '[project]\nname = "x"\nversion = "0.0.0"\n'
        assert module.sync_text(existing, new) == existing

    def test_tag_format_survives_update(self) -> None:
        """Worse than the version reset it sits beside: semantic-release
        derives the current version from tags matching `tag_format`, not from
        `project.version` — so restoring only the version leaves a repo that
        looks correct and still computes 0.1.0."""
        module = self._load_module()
        existing = '[tool.semantic_release]\ntag_format = "v{version}"\nbranch = "main"\n'
        new = '[tool.semantic_release]\ntag_format = "{version}"\nbranch = "main"\n'
        merged = module.sync_text(existing, new)
        assert 'tag_format = "v{version}"' in merged
        assert 'branch = "main"' in merged  # everything else still tracks the fresh render

    def test_table_scan_survives_build_command_shell_guards(self) -> None:
        """`build_command` is a multi-line string whose `set -e` guards start
        at column 0 with `[ -n "$UV_..." ]`. A naive `^\\[` table-end scan stops
        there — before `tag_format` — and preservation silently does nothing."""
        module = self._load_module()
        body = '[ -n "$UV_CACHE_DIR" ] || unset UV_CACHE_DIR\nuv build\n'
        existing = f'[tool.semantic_release]\nbuild_command = """\n{body}"""\ntag_format = "v{{version}}"\n'
        new = f'[tool.semantic_release]\nbuild_command = """\n{body}"""\ntag_format = "{{version}}"\n'
        assert 'tag_format = "v{version}"' in module.sync_text(existing, new)

    def test_absent_scalar_keeps_fresh_seed(self) -> None:
        """Newly enabling `use_semantic_release` gives the destination no
        `[tool.semantic_release]` to snapshot — same rule as an unsnapshotted
        marker: keep the fresh render's own default rather than blanking it."""
        module = self._load_module()
        existing = '[project]\nname = "x"\nversion = "2.0.0"\n'
        new = '[project]\nname = "x"\nversion = "0.0.0"\n\n[tool.semantic_release]\ntag_format = "{version}"\n'
        merged = module.sync_text(existing, new)
        assert 'version = "2.0.0"' in merged
        assert 'tag_format = "{version}"' in merged

    def test_rendered_pyproject_matches_preservation_shape(self, copier_defaults: dict, project_factory) -> None:
        """Guard against a future template reformat silently disabling the
        pass above: preservation is a no-op unless the *rendered* file really
        holds these keys as single-line strings in the expected tables."""
        module = self._load_module()
        rendered = (project_factory(copier_defaults, "app") / "pyproject.toml").read_text()
        for table, key, sentinel in (
            ("project", "version", "9.9.9"),
            ("tool.semantic_release", "tag_format", "vX{version}"),
        ):
            assert module.read_scalar(rendered, table, key) is not None, f"{table}.{key} unreadable in render"
            rewritten = module.replace_scalar(rendered, table, key, sentinel)
            assert module.read_scalar(rewritten, table, key) == sentinel, f"{table}.{key} not rewritable"

    def test_markers_present_in_prek_template(self) -> None:
        content = (REPO_ROOT / "project" / "prek.toml.jinja").read_text()
        assert "# template-preserve:extra-local-hooks:start" in content
        assert "# template-preserve:extra-local-hooks:end" in content

    def test_legacy_bootstrap_preserves_data_on_first_marker_aware_update(self) -> None:
        """The critical regression caught in review (Macroscope, PR #329): a
        project generated *before* markers existed has none of the
        `# template-preserve:*` comments. Without bootstrapping, its first
        update to a marker-aware template version would silently replace
        every now-marked region with the fresh render's bare default,
        discarding real user data with zero warning — the exact class of bug
        DOT-599 was filed for, reintroduced by the fix meant to prevent it."""
        module = self._load_module()
        legacy_pyproject = (
            '[project]\nname = "x"\ndependencies = ["requests>=2.31", "pydantic>=2"]\n\n'
            '[project.scripts]\nmytool = "mytool.cli:main"\n\n'
            '[dependency-groups]\nci = ["ruff>=0.14"]\ndev = ["ipython"]\n\n'
            '[[tool.uv.index]]\nurl = "https://custom.example.com"\n\n'
            '[tool.poe.tasks]\nsetup = "uv sync"\nlint = "ruff check ."\n'
            'serve = "python -m mytool.server"\nwatch = "gh run watch"\n'
        )
        fresh = (
            '[project]\nname = "x"\n# template-preserve:dependencies:start\ndependencies = []\n'
            "# template-preserve:dependencies:end\n\n"
            "# template-preserve:project-scripts:start\n[project.scripts]\n"
            'mytool = "mytool.cli:main"\n# template-preserve:project-scripts:end\n\n'
            "# template-preserve:dependency-groups:start\n[dependency-groups]\n"
            'ci = ["ruff>=0.15"]\ndev = []\n# template-preserve:dependency-groups:end\n\n'
            "# template-preserve:tool-uv-index:start\n# template-preserve:tool-uv-index:end\n\n"
            '[tool.poe.tasks]\nsetup = "uv sync"\nlint = "ruff check ."\nwatch = "gh run watch"\n'
            "# template-preserve:extra-poe-tasks:start\n# template-preserve:extra-poe-tasks:end\n"
        )
        merged = module.sync_text(legacy_pyproject, fresh)

        import tomllib

        tomllib.loads(merged)  # must stay valid TOML
        assert '"requests>=2.31"' in merged
        assert "pydantic" in merged
        assert "custom.example.com" in merged
        assert 'serve = "python -m mytool.server"' in merged
        assert merged.count("serve = ") == 1  # moved, not duplicated

    def test_legacy_bootstrap_preserves_custom_local_hook(self) -> None:
        module = self._load_module()
        legacy_prek = (
            '[[repos]]\nrepo = "local"\n\n'
            '[[repos.hooks]]\nid = "ty"\nname = "ty type checker"\n\n'
            '[[repos.hooks]]\nid = "my-custom-check"\nname = "my custom check"\n'
            'entry = "scripts/custom-check.sh"\n\n'
            '[[repos.hooks]]\nid = "check-template-update"\nname = "check for template updates"\n'
        )
        fresh = (
            '[[repos]]\nrepo = "local"\n\n'
            '[[repos.hooks]]\nid = "ty"\nname = "ty type checker"\n\n'
            '[[repos.hooks]]\nid = "check-template-update"\nname = "check for template updates"\n\n'
            "# template-preserve:extra-local-hooks:start\n# template-preserve:extra-local-hooks:end\n"
        )
        merged = module.sync_text(legacy_prek, fresh)

        import tomllib

        tomllib.loads(merged)
        assert "my-custom-check" in merged
        assert "custom-check.sh" in merged
        assert merged.count("my-custom-check") == 1


class TestMcpRegistry:
    """Test publish_to_mcp_registry question gates MCP registry publishing workflow.

    When publish_to_mcp_registry=true (requires use_semantic_release=true),
    a standalone mcp-registry-publish.yml workflow should be generated and the
    release.yml should include an mcp-registry-publish job.
    """

    def test_mcp_registry_workflow_exists_when_enabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=true should generate mcp-registry-publish.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": True}
        project = project_factory(answers)

        assert (project / ".github" / "workflows" / "mcp-registry-publish.yml").exists()

    def test_mcp_registry_workflow_absent_when_disabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=false should not generate mcp-registry-publish.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": False}
        project = project_factory(answers)

        assert not (project / ".github" / "workflows" / "mcp-registry-publish.yml").exists()

    def test_release_yml_has_mcp_job_when_enabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=true should add mcp-registry-publish job to release.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": True}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "mcp-registry-publish" in content
        assert "mcp-registry-publish.yml" in content

    def test_release_yml_no_mcp_job_when_disabled(self, copier_defaults: dict, project_factory) -> None:
        """publish_to_mcp_registry=false should not add mcp-registry-publish job to release.yml."""
        answers = {**copier_defaults, "publish_to_mcp_registry": False}
        project = project_factory(answers)

        content = (project / ".github" / "workflows" / "release.yml").read_text()
        assert "mcp-registry-publish" not in content


class TestSkipIfExists:
    """Test _skip_if_exists preserves user changes across copier recopy.

    Uses copier recopy to simulate template re-application without needing
    a version difference. copier recopy is more aggressive than copier update
    (no 3-way merge), so if _skip_if_exists works here, it works everywhere.
    """

    @pytest.mark.slow
    def test_recopy_preserves_modified_readme(self, tmp_path: Path, copier_defaults: dict) -> None:
        """User-modified README.md should not be overwritten (core _skip_if_exists file)."""
        project = generate_project(tmp_path, copier_defaults)

        readme = project / "README.md"
        assert readme.exists()

        # User customizes README
        readme.write_text("# My Project\n\nCustom README content.\n")

        # Re-apply template
        result = subprocess.run(
            ["copier", "recopy", "--trust", "--skip-tasks", "-r", "HEAD", "--skip-answered", "--defaults", "--overwrite"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"copier recopy failed: {result.stderr}"

        content = readme.read_text()
        assert "Custom README content" in content, f"README.md was overwritten by copier recopy. Content:\n{content}"


class TestIntegration:
    """Integration tests that run uv sync and checks on generated project."""

    @staticmethod
    def _init_git_repo(project: Path) -> None:
        """Initialize a git repo with an initial commit in the given project."""
        subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: Initial commit"],
            cwd=project,
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@test.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@test.com",
            },
        )

    @pytest.mark.slow
    def test_uv_sync_succeeds(self, tmp_path: Path, copier_defaults: dict) -> None:
        """Generated project should successfully run uv sync."""
        project = generate_project(tmp_path, copier_defaults)
        self._init_git_repo(project)

        # Run uv sync
        result = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"uv sync failed: {result.stderr}"

    @pytest.mark.slow
    def test_declared_floors_actually_work(self, tmp_path: Path, copier_defaults: dict) -> None:
        """A generated project must lint, typecheck and test at its declared floors.

        Every other floor test asserts on what pyproject *says*. This one runs the
        bottom of every declared range, which is the only thing that catches a floor
        that is a lie -- the shape of both the ruff bug in #333 (`extend-select`
        assumes 0.16's defaults, floor said 0.14) and DOT-616 (prek's `[update]`
        tag filters need 0.4.10, floor said 0.3.11).

        `UV_RESOLUTION` has to be in the environment, not just on the `uv sync` line:
        `uv run` re-resolves and would silently swap the lockfile back to `highest`
        ("Ignoring existing lockfile due to change in resolution mode"), so the run
        would measure the newest releases while appearing to measure the floors.
        """
        project = generate_project(tmp_path, copier_defaults)
        env = {**os.environ, "UV_RESOLUTION": "lowest-direct"}

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False, env=env)
        assert sync.returncode == 0, f"uv sync at declared floors failed: {sync.stderr}"

        for task in ("lint", "typecheck", "test"):
            result = subprocess.run(["uv", "run", "poe", task], cwd=project, capture_output=True, text=True, check=False, env=env)
            assert result.returncode == 0, f"`poe {task}` failed at the declared dependency floors:\n{result.stdout}\n{result.stderr}"

    @pytest.mark.slow
    def test_test_cov_produces_a_report(self, tmp_path: Path, copier_defaults: dict) -> None:
        """`poe test-cov` must produce an actual report on a freshly generated project.

        The bug this pins (DOT-617) was silent in the worst way: coverage measured
        `src/`, an `omit = ["src/*/__init__.py"]` pattern excluded the only Python
        file a fresh project has, and coverage was left with nothing to report. It
        emitted a CovReportWarning, wrote neither the terminal table nor `htmlcov/`,
        and exited 0 -- so the task looked like it worked.

        Every other coverage assertion in this suite reads pyproject *content*.
        This one runs the task, which is the only way to catch a config that is
        internally consistent but produces nothing.
        """
        project = generate_project(tmp_path, copier_defaults)

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

        result = subprocess.run(
            ["uv", "run", "poe", "test-cov"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"`poe test-cov` failed:\n{result.stdout}\n{result.stderr}"

        # Exit code 0 is not enough -- that is exactly what the bug produced.
        output = result.stdout + result.stderr
        assert "No data to report" not in output, f"coverage had nothing to measure:\n{output}"
        assert "TOTAL" in output, f"coverage terminal report was not written:\n{output}"
        assert (project / "htmlcov" / "index.html").exists(), "coverage HTML report was not written"

    @pytest.mark.slow
    def test_first_commit_succeeds_with_prek_hooks(self, tmp_path: Path, copier_defaults: dict) -> None:
        """First `git commit` on a freshly scaffolded project must succeed.

        Reproduces the exact user flow from a fresh folder:
            copier copy ... && cd <dest>
            uv sync
            git init && uv run prek install && uv run prek update
            git add -A && git commit -m "feat: init commit"

        Originally added as a regression test for DOT-491 (pytest-testmon hook exited 5
        because the template shipped no tests/). Intentionally runs the FULL prek hook
        chain with no SKIP -- if any hook fails on a freshly scaffolded project, the
        template is broken from the user's perspective and we have work to do.
        """
        project = generate_project(tmp_path, copier_defaults)

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

        git_env: dict[str, str] = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@test.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@test.com",
        }
        # An ambient SKIP=... in the developer's shell or CI step would silently
        # disable prek hooks and defeat the whole point of this regression test.
        git_env.pop("SKIP", None)

        subprocess.run(
            ["git", "init", "--initial-branch=main"],
            cwd=project,
            check=True,
            capture_output=True,
        )
        install = subprocess.run(
            ["uv", "run", "prek", "install"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert install.returncode == 0, f"prek install failed: {install.stderr}"
        update = subprocess.run(
            ["uv", "run", "prek", "update"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update.returncode == 0, f"prek update failed: {update.stderr}"

        # The whole point of moving the lychee exclusion into prek.toml is that a
        # bare `prek update` -- the one a user actually types -- is safe. Assert
        # on the outcome rather than on the config, which is checked separately.
        with (project / "prek.toml").open("rb") as f:
            lychee = next(r for r in tomllib.load(f)["repos"] if r.get("repo", "").endswith("/lychee"))
        assert lychee["rev"].startswith("lychee-v"), f"`prek update` flipped lychee to a mutable tag: {lychee['rev']!r} (DOT-492, DOT-616)"

        # Mirror the real user flow: hooks may auto-fix files (formatters, lockfile sync)
        # on the first run, abort the commit, and the user re-stages and retries.
        # Allow up to 2 attempts; the second must succeed.
        for attempt in (1, 2):
            subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
            commit = subprocess.run(
                ["git", "commit", "-m", "feat: init commit"],
                cwd=project,
                capture_output=True,
                text=True,
                check=False,
                env=git_env,
            )
            if commit.returncode == 0:
                break
            assert attempt == 1, (
                f"first commit on freshly scaffolded project failed after re-stage:\nstdout:\n{commit.stdout}\nstderr:\n{commit.stderr}"
            )

    @pytest.mark.slow
    def test_update_preserves_uv_lock_and_venv_across_versions(self, tmp_path: Path, copier_defaults: dict) -> None:
        """`copier update` from an old template version must not delete the user's `uv.lock` or trash `.venv` (DOT-587, DOT-588).

        Regression scenario:
          - User's project was scaffolded on template ≤0.34.3, which ran an unguarded
            `uv sync` in `_tasks`. So copier's `old_copy` temp render produces `uv.lock` and
            a full `.venv/` tree.
          - On update to a fixed template, copier compares `old_copy` vs `new_copy` and
            removes from the destination anything present only in old_copy. Without the
            inverted-guard fix (see `test_uv_sync_task_runs_in_copier_temp_render_dirs`),
            new_copy lacks both → `uv.lock` is deleted and `.venv` is mauled.

        This test runs the full flow against the real 0.34.3 tag and the current HEAD,
        skipping if the tag is absent (e.g. shallow clones in CI).
        """
        repo_root = pathlib.Path(__file__).resolve().parent.parent

        # Need the 0.34.3 tag to render the "old" baseline. Skip if a shallow clone is
        # missing it rather than fail spuriously.
        tag_check = subprocess.run(
            ["git", "rev-parse", "--verify", "0.34.3"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if tag_check.returncode != 0:
            pytest.skip("0.34.3 tag not available in this checkout (shallow clone?)")

        project = tmp_path / "proj"

        # Render at 0.34.3, the version with the unguarded `uv sync` task. `--skip-tasks`
        # because we'll set up the venv ourselves in a controlled way below.
        cmd = [
            "copier",
            "copy",
            "--trust",
            "--skip-tasks",
            "-f",
            "-r",
            "0.34.3",
            str(repo_root),
            str(project),
        ]
        defaults = {**copier_defaults, "project_type": "app"}
        for k, v in defaults.items():
            cmd.extend(["-d", f"{k}={str(v).lower() if isinstance(v, bool) else v}"])
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"copier copy at 0.34.3 failed: {result.stderr}"

        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
        subprocess.run(["git", "add", "-A"], cwd=project, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=project, env=git_env, check=True)

        # Populate the user's local state: real `uv.lock` and `.venv` from `uv sync`.
        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed during setup: {sync.stderr}"
        assert (project / "uv.lock").is_file(), "Setup precondition: uv.lock should exist after uv sync"
        assert (project / ".venv" / "pyvenv.cfg").is_file(), "Setup precondition: .venv/pyvenv.cfg should exist after uv sync"
        subprocess.run(["git", "add", "uv.lock"], cwd=project, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "add uv.lock", "--no-verify"],
            cwd=project,
            env=git_env,
            check=False,
        )

        # Run the update against current HEAD (which must contain the fix).
        update = subprocess.run(
            ["copier", "update", "--trust", "--defaults", "--conflict", "rej", "--vcs-ref", "HEAD"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert update.returncode == 0, f"copier update failed:\nstdout:\n{update.stdout}\nstderr:\n{update.stderr}"

        # Core assertions — both files must survive the update.
        assert (project / "uv.lock").is_file(), (
            "uv.lock was deleted by `copier update` — DOT-587 regression. Check the `uv sync` task guard in copier.yml _tasks."
        )
        assert (project / ".venv" / "pyvenv.cfg").is_file(), (
            ".venv/pyvenv.cfg disappeared after `copier update` — DOT-588 regression. "
            "`uv sync` in the destination's venv would now error with "
            "'cannot be recreated because it is not a virtual environment'."
        )

    @pytest.mark.slow
    def test_semantic_release_writes_gitlab_urls_for_selfhosted(self, tmp_path: Path, copier_defaults: dict) -> None:
        """semantic-release must write GitLab-format commit URLs into CHANGELOG.md when `repository_provider=gitlab.com` (DOT-590).

        Static config tests (`test_gitlab_semantic_release_remote`,
        `test_gitlab_selfhosted_semantic_release_remote_domain`) cover the rendered TOML, but
        they don't catch the case where python-semantic-release ignores or misinterprets the
        config and falls back to GitHub URL conventions — exactly the symptom the user saw
        (their existing CHANGELOG had `github.com/<namespace>/<pkg>/commit/<sha>` for a GitLab
        project). This is the end-to-end check: actually run `semantic-release changelog` on
        a multi-level GitLab self-hosted setup and verify the URL format.
        """
        answers = {
            **copier_defaults,
            "repository_provider": "gitlab.com",
            "repository_host": "gitlab.pnet.ch",
            "repository_namespace": "kop/ismar",
            "project_name": "Die Zeit",
            "open_source": False,
        }
        project = generate_project(tmp_path, answers)

        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "git@gitlab.pnet.ch:kop/ismar/die-zeit.git"],
            cwd=project,
            check=True,
        )
        subprocess.run(["git", "add", "-A"], cwd=project, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "feat: initial commit", "--no-verify"],
            cwd=project,
            env=git_env,
            check=True,
        )

        sync = subprocess.run(["uv", "sync"], cwd=project, capture_output=True, text=True, check=False)
        assert sync.returncode == 0, f"uv sync failed: {sync.stderr}"

        # Make a real feat commit so semantic-release has something to changelog.
        (project / "foo.txt").write_text("x\n")
        subprocess.run(["git", "add", "foo.txt"], cwd=project, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "feat: add foo", "--no-verify"],
            cwd=project,
            env=git_env,
            check=True,
        )

        result = subprocess.run(
            ["uv", "run", "semantic-release", "changelog"],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"semantic-release changelog failed: {result.stderr}"

        changelog = (project / "CHANGELOG.md").read_text()

        # Positive: at least one correctly-formatted gitlab self-hosted commit URL exists.
        assert "https://gitlab.pnet.ch/kop/ismar/die-zeit/-/commit/" in changelog, (
            f"Expected gitlab self-hosted commit URL in CHANGELOG.md. Got:\n{changelog}"
        )

        # Negative: no github.com URLs leaked into the gitlab project's changelog (DOT-590).
        assert "github.com" not in changelog, f"github.com URL leaked into a gitlab project's CHANGELOG.md (DOT-590):\n{changelog}"

        # Negative: no underscore form of the repo slug (the user's specific symptom — `die_zeit`
        # instead of `die-zeit`). semantic-release should derive the slug from the git remote
        # URL, never from python_package_import_name.
        assert "die_zeit" not in changelog, (
            f"Underscored repo slug `die_zeit` leaked into CHANGELOG.md — semantic-release "
            f"appears to be using python_package_import_name instead of the repo slug:\n{changelog}"
        )
