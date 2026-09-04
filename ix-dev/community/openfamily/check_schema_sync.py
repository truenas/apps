#!/usr/bin/env python3
"""Diff the vendored OpenFamily base schema against the tagged upstream release.

Not part of the rendering pipeline and never run by CI (no test in this repo
touches the network). Run manually before bumping this app's `app_version`:

    python3 ix-dev/community/openfamily/check_schema_sync.py

The vendored copy lives in templates/macros/schema.sql because the published
server image only ships incremental "ADD COLUMN IF NOT EXISTS" migrations on
top of it, not the base tables (see server/src/db.ts upstream). If this script
reports drift, update that macro to match and re-render the app.
"""
import difflib
import re
import sys
import urllib.request
from pathlib import Path

APP_DIR = Path(__file__).parent
UPSTREAM_REPO = "NexaFlowFrance/OpenFamily"
UPSTREAM_PATH = "server/schema.sql"


def get_app_version() -> str:
    app_yaml = (APP_DIR / "app.yaml").read_text()
    match = re.search(r'^app_version:\s*"?([^"\n]+?)"?\s*$', app_yaml, re.MULTILINE)
    if not match:
        sys.exit("Could not find app_version in app.yaml")
    return match.group(1)


def get_our_schema() -> str:
    macro = (APP_DIR / "templates/macros/schema.sql").read_text()
    match = re.search(r"\{%\s*macro schema\(\)\s*-%\}\n(.*)\n\{%-\s*endmacro\s*%\}", macro, re.DOTALL)
    if not match:
        sys.exit("Could not extract the schema() macro body from templates/macros/schema.sql")
    return match.group(1)


def get_upstream_schema(tag: str) -> str:
    url = f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{tag}/{UPSTREAM_PATH}"
    with urllib.request.urlopen(url, timeout=15) as resp:  # noqa: S310
        return resp.read().decode("utf-8")


def sql_statement_lines(text: str) -> list[str]:
    """Drop comment-only and blank lines so wording/formatting tweaks upstream
    (like the mojibake em-dashes in their comments as of v1.6.0) don't get
    flagged as drift - only actual schema changes should."""
    return [line for line in text.splitlines() if line.strip() and not line.strip().startswith("--")]


def main() -> int:
    version = get_app_version()
    tag = f"v{version}"
    print(f"Comparing templates/macros/schema.sql against {UPSTREAM_REPO}@{tag}:{UPSTREAM_PATH}")

    ours = get_our_schema()
    upstream = get_upstream_schema(tag)
    ours_lines = sql_statement_lines(ours)
    upstream_lines = sql_statement_lines(upstream)

    if ours_lines == upstream_lines:
        print("OK: vendored schema statements match upstream (comment-only differences ignored).")
        return 0

    print(f"DRIFT DETECTED between our vendored schema and upstream {tag}:\n")
    diff = difflib.unified_diff(
        [line + "\n" for line in ours_lines],
        [line + "\n" for line in upstream_lines],
        fromfile="ours (templates/macros/schema.sql)",
        tofile=f"upstream {tag} ({UPSTREAM_PATH})",
    )
    sys.stdout.writelines(diff)
    return 1


if __name__ == "__main__":
    sys.exit(main())
