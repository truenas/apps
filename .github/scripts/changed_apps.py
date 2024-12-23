#!/usr/bin/env python3

import pathlib
import json
import sys
import re

APP_REGEX = re.compile(r"^ix-dev\/([-\w\.]+)\/([-\w\.]+)")
TEST_VALUES_DIR = "templates/test_values"
OUTPUT_FILE = ".github/outputs/all_changed_files.json"
EXCLUDE_TESTS = [
    "stable/storj",
]


def get_changed_files():
    with open(OUTPUT_FILE, "r") as f:
        json_files = f.read()

    if not json_files:
        print(f"File [{OUTPUT_FILE}] is empty", file=sys.stderr)
        exit(1)

    try:
        return json.loads(json_files.replace("\\", ""))
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from [{OUTPUT_FILE}] file", file=sys.stderr)
        exit(1)


def find_test_files(changed_files):
    seen = set()
    matrix = []
    skipped = set()
    for file in changed_files:
        match = APP_REGEX.match(file)
        if not match:
            continue

        full_name = f"{match.group(1)}/{match.group(2)}"
        if full_name in EXCLUDE_TESTS:
            if full_name not in skipped:
                skipped.add(full_name)
            continue
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

    if skipped:
        print("Skipped apps based on the EXCLUDE_TESTS list:", file=sys.stderr)
        print("\n".join(skipped), file=sys.stderr)

    result = {
        "matrix1": {"include": matrix[:256]},
        "matrix2": {"include": matrix[256:]},
    }

    return json.dumps(result)


def main():
    changed_files = get_changed_files()
    print(find_test_files(changed_files))
    # This should look like:
    # {
    #   "matrix1": {
    #     "include": [
    #       { "train": "enterprise", "app": "minio", "test_file": "basic-values.yaml" },
    #       { "train": "enterprise", "app": "minio", "test_file": "https-values.yaml" },
    #       ...
    #     ]
    #   },
    #   "matrix2": {
    #     "include": [
    #       { "train": "enterprise", "app": "minio", "test_file": "basic-values.yaml" },
    #       { "train": "enterprise", "app": "minio", "test_file": "https-values.yaml" },
    #       ...
    #     ]
    #   }
    # }


if __name__ == "__main__":
    main()
