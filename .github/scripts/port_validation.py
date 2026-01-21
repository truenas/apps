#!/usr/bin/python3

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import sys
import yaml

from collections import defaultdict
from os import scandir


def extract_ports_from_items(items):
    ports = []

    for item in items:
        if not item_looks_like_port(item):
            continue
        ports.append({"name": item["variable"], "port": item["schema"]["default"]})

    return ports


def item_looks_like_port(item):
    schema = item["schema"]
    if schema["type"] != "int":
        return False
    if schema.get("min", 0) != 1:
        return False
    if schema.get("max", 0) != 65535:
        return False
    if not schema.get("default"):
        return False
    return True


def dict_looks_like_port(attrs):
    for var in attrs:
        if var["variable"] == "host_ips":
            return True
    return False


def extract_ports(quests):
    ports = []
    for quest in quests:
        port_name = None
        schema = quest["schema"]
        if quest["variable"].endswith("_port"):
            port_name = quest["variable"]

        start_idx = len(ports)  # Track starting point

        if schema["type"] == "dict":
            if dict_looks_like_port(schema["attrs"]):
                ports.extend(extract_ports_from_items(schema["attrs"]))
            else:
                ports.extend(extract_ports(schema["attrs"]))
        elif schema["type"] == "list":
            ports.extend(extract_ports(schema["items"]))

        if port_name:
            for port in ports[start_idx:]:  # Only new ports
                port["name"] = port_name

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
    port_docs = []
    for path in filter(lambda x: x.endswith("questions.yaml"), scan_directory("ix-dev")):
        with open(path) as f:
            parts = path.split("/")
            app_info = f"{parts[-3]}/{parts[-2]}"
            for item in extract_ports(yaml.load(f, Loader=yaml.FullLoader)["questions"]):
                app_port, port_name = item["port"], item["name"]
                port_map[app_port].append(f"{app_info} ({port_name})")
                port_docs.append((app_info, port_name, app_port))
                if len(port_map[app_port]) > 1 and app_port not in ignore_ports:
                    dupe_found = True
                    dup_apps = ", ".join(port_map[app_port])
                    print(f"Duplicate port [{app_port}] in apps: {dup_apps}")
    return port_map, dupe_found, port_docs


def main():
    start_range, max_range = 30000, 40000
    port_map, dupe_found, port_docs = get_current_port_map()
    next_5_avail_ports = sorted(list(set(range(start_range, max_range + 1)) - set(port_map)))[:5]
    print(f"Next 5 available ports: [{', '.join([str(x) for x in next_5_avail_ports])}]")
    if dupe_found:
        print("Duplicate ports found, please use one of the available ports.")
        sys.exit(1)
    if len(sys.argv) > 1 and sys.argv[1] == "docs":
        print("Ports with documentation:")
        for app_info, port_name, app_port in port_docs:
            print(f"{app_info},{port_name},{app_port}")


if __name__ == "__main__":
    main()
