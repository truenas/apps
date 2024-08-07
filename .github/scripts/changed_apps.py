#!/usr/bin/env python3

import pathlib
import json
import sys
import os
import re

APP_REGEX = re.compile(r"^ix-dev\/([-\w\.]+)\/([-\w\.]+)")
TEST_VALUES_DIR = "templates/test_values"


def get_changed_files():
    json_files = os.getenv("CHANGED_FILES", "")
    if not json_files:
        print("Environment variable CHANGED_FILES is empty", file=sys.stderr)
        exit(1)

    try:
        return json.loads(json_files.replace("\\", ""))
    except json.JSONDecodeError:
        print("Failed to decode JSON from CHANGED_FILES", file=sys.stderr)
        exit(1)


def find_test_files(changed_files):
    seen = set()
    matrix = []
    for file in changed_files:
        match = APP_REGEX.match(file)
        if not match:
            continue

        full_name = f"{match.group(1)}/{match.group(2)}"
        for file in pathlib.Path("ix-dev", full_name, TEST_VALUES_DIR).glob("*.yaml"):
            item_tuple = (match.group(1), match.group(2), file.name)
            if item_tuple not in seen:
                print(
                    f"Detected changed item for [{full_name}] adding [{file.name}] to matrix",
                    file=sys.stderr,
                )
                seen.add(item_tuple)
                matrix.append(
                    {
                        "train": match.group(1),
                        "app": match.group(2),
                        "test_file": file.name,
                    }
                )

    return matrix


def main():
    changed_files = get_changed_files()
    matrix = find_test_files(changed_files)
    # This should look like:
    # {
    #   "include": [
    #     { "train": "enterprise", "app": "minio", "test_file": "basic-values.yaml" },
    #     { "train": "enterprise", "app": "minio", "test_file": "https-values.yaml" },
    #     ...
    #   ]
    # }

    print(json.dumps({"include": matrix}))


if __name__ == "__main__":
    main()
