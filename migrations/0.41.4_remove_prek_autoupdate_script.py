"""Migration for the 0.41.4 release: delete the orphaned
`scripts/prek-autoupdate.sh`.

0.41.4 replaced that wrapper with a declarative `[update.repos]` tag filter in
`prek.toml`, available since prek 0.4.10. `copier update` never deletes files,
so without this migration every existing project keeps a script that still
works but is no longer referenced by `poe update-template` or the docs -- and
which pins the old `--repo-exclude-tag` approach that the config now covers for
every invocation rather than only the wrapped one. See DOT-616.

Runs as a `_migrations` "after" step (see copier.yml) so the file is removed
once the rest of the update has been applied.

Deliberately narrow: it removes the file only when the content is byte-for-byte
one of the versions the template shipped. A project that edited the script had a
reason to, and silently discarding that is worse than leaving a stale file
behind -- the user can delete it themselves once they notice it is unreferenced.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

SCRIPT = Path("scripts") / "prek-autoupdate.sh"

# SHA-256 of every version of this script the template ever shipped. An exact
# digest rather than a substring match in either direction:
#
#   - A substring guard deletes a script a user really did edit, as long as the
#     matched line survived. Deleting someone's work on a heuristic is the one
#     outcome this migration must not have.
#   - It also misses whole shipped versions. The pre-DOT-540 script used a
#     second `--cooldown-days 7` pass and contains no `--repo-exclude-tag` at
#     all, so a marker-based guard would flag every project generated before
#     0.40.0 as "customised" and leave a pristine file behind with a warning.
#
# The script carries no `.jinja` suffix, so copier copies it verbatim rather
# than rendering it -- the bytes are identical in every generated project,
# which is what makes hashing exact here rather than approximate.
TEMPLATE_DIGESTS = frozenset(
    {
        # 0.38.1 (aa0ccfa, DOT-492): two-pass autoupdate, second pass --cooldown-days 7
        "d8388e2e64b314dab77b45a1f394a2d2ef5b0e5830357f9d7f95004eea5031bb",
        # 0.40.0 (e452c32, DOT-540): single pass, --repo-exclude-tag
        "23cb6d83048dfbd8b65304a5807a15223727c5d69bd412c0dbd37f7e9909a8c5",
    }
)


def main() -> None:
    if not SCRIPT.is_file():
        return

    # Normalise line endings before hashing: a Windows checkout with
    # `core.autocrlf=true` stores the same shipped file with CRLF, which would
    # otherwise read as a customisation.
    body = SCRIPT.read_bytes().replace(b"\r\n", b"\n")

    if hashlib.sha256(body).hexdigest() not in TEMPLATE_DIGESTS:
        print(f"  ⚠ {SCRIPT} differs from every version this template shipped — leaving it in place.")
        print("    It is no longer referenced by `poe update-template`; the lychee `nightly`")
        print("    exclusion now lives in prek.toml, so the script can be deleted once you agree.")
        return

    SCRIPT.unlink()
    print(f"  ✓ Removed {SCRIPT} — the lychee `nightly` exclusion now lives in prek.toml")


if __name__ == "__main__":
    main()
