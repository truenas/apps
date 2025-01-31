#!/usr/bin/python3

import sys
import yaml
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


def main():
    port_map = {}
    for path in scan_directory("ix-dev"):
        if not path.endswith("questions.yaml"):
            continue
        with open(path, "r") as f:
            train = path.split("/")[-3]
            app = path.split("/")[-2]
            ports_data = extract_ports(yaml.load(f, Loader=yaml.FullLoader)["questions"])
            for item in ports_data:
                port_num = item["port"]
                if port_num not in port_map:
                    port_map[port_num] = []
                port_map[port_num].append(f"{train}/{app} ({item['name']})")

    ignore_ports = [53, 22000]
    dupe_found = False
    for port, apps in port_map.items():
        if len(apps) > 1 and (port not in ignore_ports):
            dupe_found = True
            print(f"Duplicate port [{port}] in apps: {', '.join(apps)}")

    ports_in_range = sorted(p for p in port_map if 30000 <= p <= 40000)
    next_five_available = []
    for port in ports_in_range:
        if len(next_five_available) == 5:
            break
        next_port = port + 1
        if next_port in port_map:
            continue
        next_five_available.append(str(next_port))

    print(f"Next 5 available ports: [{', '.join(next_five_available)}]")

    if dupe_found:
        print("Duplicate ports found, please use one of the available ports.")
        sys.exit(1)


if __name__ == "__main__":
    main()
