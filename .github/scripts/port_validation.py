#!/usr/bin/python3

import sys
import yaml

from collections import defaultdict
from os import scandir


def extract_ports(quests):
    ports = []
    for quest in quests:
        schema = quest["schema"]
        if schema["type"] == "int" and "definitions/port" in schema.get("$ref", []) and "default" in schema:
            ports.append({"name": quest["variable"], "port": schema["default"]})
        elif schema["type"] == "dict":
            ports.extend(extract_ports(schema["attrs"]))
        elif schema["type"] == "list":
            ports.extend(extract_ports(schema["items"]))

    return ports


def scan_directory(path: str, current_depth: int = 0, to_depth: int = 2):
    """Iterate over `path` to depth level `to_depth`
    and yield any file paths at that level."""
    if current_depth > to_depth:
        return

    with scandir(path) as sdir:
        for entry in sdir:
            if current_depth == to_depth and entry.is_file():
                yield entry.path
            elif (current_depth < to_depth) and entry.is_dir():
                yield from scan_directory(entry.path, current_depth + 1)


def get_current_port_map():
    port_map = defaultdict(list)
    ignore_ports = (53, 22000)
    dupe_found = False
    for path in filter(lambda x: x.endswith("questions.yaml"), scan_directory("ix-dev")):
        with open(path) as f:
            parts = path.split("/")
            app_info = f"{parts[-3]}/{parts[-2]}"
            for item in extract_ports(yaml.load(f, Loader=yaml.FullLoader)["questions"]):
                app_port, app_name = item["port"], item["name"]
                port_map[app_port].append(f"{app_info} ({app_name})")
                if len(port_map[app_port]) > 1 and app_port not in ignore_ports:
                    dupe_found = True
                    dup_apps = ", ".join(port_map[app_port])
                    print(f"Duplicate port [{app_port}] in apps: {dup_apps}")
    return port_map, dupe_found


def main():
    start_range, max_range = 30000, 40000
    port_map, dupe_found = get_current_port_map()
    next_5_avail_ports = sorted(list(set(range(start_range, max_range + 1)) - set(port_map)))[:5]
    print(f"Next 5 available ports: [{', '.join([str(x) for x in next_5_avail_ports])}]")
    if dupe_found:
        print("Duplicate ports found, please use one of the available ports.")
        sys.exit(1)


if __name__ == "__main__":
    main()
