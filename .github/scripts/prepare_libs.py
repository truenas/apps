#!/usr/bin/env python3
"""
Put the libraries the apps render with in place

Copies each app's base library (library/<lib_version>) to templates/library/base_v<version> and its own
library source (lib/) to templates/library/<train>/<app>/v<version>, the paths the renderer imports them from.
Publish builds the same libraries into the trains itself, these copies are only for validating and rendering.
lib_version_hash is left alone, so a library changed without updating it still fails the catalog validation.

Apps with a lib/ also get lib/ix_lib/base, a symlink to their base_v<version> copy, and lib/ix_lib/values.py, the
TypedDicts of their values generated from questions.yaml and ix_values.yaml. Pyright resolves imports from the
importing file's directory, so `from ix_lib.base/values import ...` (under TYPE_CHECKING) gets the exact library
version and values the app uses, with no type checker config. Both are gitignored and never copied or published.
"""

import os

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
from values_types import generate_values_types

# Never part of a library, same as the catalog's hash generation and publish leave out
EXCLUDED_NAMES = ("tests", "__pycache__")
# lib/<TYPING_ALIAS>/base -> the app's base library copy, for type checking only
TYPING_ALIAS = "ix_lib"


def link_typing_alias(app_path: Path, app_lib_path: Path, base_lib_copy: Path) -> None:
    alias_dir = app_lib_path / TYPING_ALIAS
    alias_dir.mkdir(exist_ok=True)
    link = alias_dir / "base"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(os.path.relpath(base_lib_copy, alias_dir), target_is_directory=True)
    # ix_lib.values: the TypedDicts of the values the app renders with
    (alias_dir / "values.py").write_text(generate_values_types(app_path))


def prepare_app_libs(app_path: Path) -> None:
    app_config = read_yaml(app_path / APP_METADATA_FILE)
    library_path = app_path / "templates/library"
    app_lib_path = app_path / APP_LIBRARY_SOURCE_DIR

    if lib_version := app_config.get("lib_version"):
        base_lib_path = LIBRARY_DIR / lib_version
        if not base_lib_path.is_dir():
            raise ValueError(f"library version {lib_version} not found in {LIBRARY_DIR}")
        for old_base_lib in library_path.glob("base_*"):
            shutil.rmtree(old_base_lib)
        base_lib_copy = library_path / f"base_v{lib_version.replace('.', '_')}"
        shutil.copytree(base_lib_path, base_lib_copy, ignore=shutil.ignore_patterns(*EXCLUDED_NAMES))
        if app_lib_path.is_dir():
            link_typing_alias(app_path, app_lib_path, base_lib_copy)

    if app_lib_path.is_dir():
        train_lib_path = library_path / app_config["train"]
        shutil.rmtree(train_lib_path, ignore_errors=True)
        shutil.copytree(
            app_lib_path,
            train_lib_path / app_config["name"] / f"v{app_config['version'].replace('.', '_')}",
            ignore=shutil.ignore_patterns(*EXCLUDED_NAMES, TYPING_ALIAS),
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
