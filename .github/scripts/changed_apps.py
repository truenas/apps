#!/usr/bin/env python3

import pathlib
import json
import sys
import os
import re

# Train and App name can contain:
# - alphanumeric characters
# - dots, dashes and underscores
APP_REGEX = re.compile(r"^ix-dev\/([-\w\.]+)\/([-\w\.]+)")
TEST_VALUES_DIR = "test_values"

# Get the changed files (json formatted)
json_files = os.getenv("CHANGED_FILES")
if json_files == "":
    print("Environment variable CHANGED_FILES is empty", file=sys.stderr)
    exit(1)

print(f"Current working directory: {os.getcwd()}", file=sys.stderr)

# Remove escaped backslashes coming from shell
json_files = json_files.replace("\\", "")
# Print to stderr, in order to keep stdout only for data
print(f"Changed files: {json_files}", file=sys.stderr)

# Parse the json
changed_files = json.loads(json_files)

result = {}
for file in changed_files:
    match = APP_REGEX.match(file)
    if not match:
        continue

    full_name = f"{match.group(1)}/{match.group(2)}"
    if full_name in result:
        continue

    result[full_name] = {
        "train": match.group(1),
        "app": match.group(2),
        "test_values": [
            file.name
            for file in pathlib.Path(
                # ix-dev/{train}/{app}/test_values/*.yaml
                "ix-dev",
                match.group(1),
                match.group(2),
                TEST_VALUES_DIR,
            ).glob("*.yaml")
        ],
    }

    print(
        f"Detected changed item for {full_name}: {json.dumps(result[full_name], indent=2)}",
        file=sys.stderr,
    )


print(json.dumps(result))
