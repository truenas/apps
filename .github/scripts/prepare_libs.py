#!/usr/bin/env python3
"""
Put the libraries the apps render with in place

Copies each app's base library (library/<lib_version>) to templates/library/base_v<version> and its own
library source (lib/) to templates/library/<train>/<app>/v<version>, the paths the renderer imports them from.
Publish builds the same libraries into the trains itself, these copies are only for validating and rendering.
lib_version_hash is left alone, so a library changed without updating it still fails the catalog validation.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import argparse
import shutil
import sys
from pathlib import Path

from common import APP_LIBRARY_SOURCE_DIR, APP_METADATA_FILE, APPS_ROOT_DIR, LIBRARY_DIR, read_yaml

# Never part of a library, same as the catalog's hash generation and publish leave out
EXCLUDED_NAMES = ("tests", "__pycache__")


def prepare_app_libs(app_path: Path) -> None:
    app_config = read_yaml(app_path / APP_METADATA_FILE)
    library_path = app_path / "templates/library"

    if lib_version := app_config.get("lib_version"):
        base_lib_path = LIBRARY_DIR / lib_version
        if not base_lib_path.is_dir():
            raise ValueError(f"library version {lib_version} not found in {LIBRARY_DIR}")
        for old_base_lib in library_path.glob("base_*"):
            shutil.rmtree(old_base_lib)
        shutil.copytree(
            base_lib_path,
            library_path / f"base_v{lib_version.replace('.', '_')}",
            ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
        )

    app_lib_path = app_path / APP_LIBRARY_SOURCE_DIR
    if app_lib_path.is_dir():
        train_lib_path = library_path / app_config["train"]
        shutil.rmtree(train_lib_path, ignore_errors=True)
        shutil.copytree(
            app_lib_path,
            train_lib_path / app_config["name"] / f"v{app_config['version'].replace('.', '_')}",
            ignore=shutil.ignore_patterns(*EXCLUDED_NAMES),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy the base and app libraries into the apps")
    parser.add_argument("--train", help="Specific train name to process")
    parser.add_argument("--app", help="Specific app name to process (requires --train)")
    args = parser.parse_args()

    if bool(args.train) != bool(args.app):
        parser.error("Both --train and --app must be provided together, or neither")

    if args.train:
        app_paths = [APPS_ROOT_DIR / args.train / args.app]
    else:
        app_paths = sorted(p.parent for p in APPS_ROOT_DIR.glob(f"*/*/{APP_METADATA_FILE}"))

    failed = False
    for app_path in app_paths:
        try:
            prepare_app_libs(app_path)
        except Exception as e:
            print(f"Failed to prepare the libraries of {app_path}: {e}", file=sys.stderr)
            failed = True

    print(f"Prepared the libraries of {len(app_paths)} apps")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
