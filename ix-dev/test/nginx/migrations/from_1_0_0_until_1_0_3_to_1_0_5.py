#!/usr/bin/python3

import os
import sys
import yaml


def migrate(values):
    with open("/tmp/migrations/from_1_0_0_until_1_0_3_to_1_0_5.txt", "w") as f:
        f.write(yaml.dump(values))
    return values


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(1)

    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r") as f:
            print(yaml.dump(migrate(yaml.safe_load(f.read()))))
