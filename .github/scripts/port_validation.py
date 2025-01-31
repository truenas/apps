#!/usr/bin/python3

import os
import sys
import yaml


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


def main():
    port_map = {}
    for train in os.listdir("ix-dev"):
        for app in os.listdir(f"ix-dev/{train}"):
            quest_path = f"ix-dev/{train}/{app}/questions.yaml"
            if not os.path.exists(quest_path):
                continue

            with open(f"ix-dev/{train}/{app}/questions.yaml", "r") as f:
                ports = extract_ports(yaml.load(f, Loader=yaml.FullLoader)["questions"])
                for port in ports:
                    port_num = port["port"]
                    if port_num not in port_map:
                        port_map[port_num] = []
                    port_map[port_num].append(app)

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
