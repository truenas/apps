#!/usr/bin/env python3
"""Fail if an app's generated metadata (app.yaml, item.yaml) is not up to date."""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import argparse
import subprocess
import sys

import generate_metadata
from common import APPS_ROOT_DIR


def git_diff(path) -> str:
    return subprocess.run(["git", "diff", "--", str(path)], capture_output=True, text=True, check=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, help="The name of the train for the app")
    parser.add_argument("--app", required=True, help="The name of the app")
    args = parser.parse_args()

    app_path = APPS_ROOT_DIR / args.train / args.app
    app = generate_metadata.load_app(args.train, app_path)
    if not app:
        print(f"App [{app_path}] has no metadata to check")
        return

    # Compare against the diff before the run, so uncommitted local changes don't count
    before = git_diff(app_path)
    try:
        generate_metadata.update_app(app, bump_version=True, set_date_added=False)
    except Exception as e:
        print(f"Metadata generation for [{args.train}/{args.app}] failed: {e}")
        sys.exit(1)

    after = git_diff(app_path)
    if before != after:
        print(after)
        print(f"Metadata of [{args.train}/{args.app}] is not up to date")
        print(
            f"Please run [python3 ./.github/scripts/generate_metadata.py --train {args.train} --app {args.app}]"
            " and commit the changes"
        )
        sys.exit(1)

    print(f"Metadata of [{args.train}/{args.app}] is up to date")


if __name__ == "__main__":
    main()
