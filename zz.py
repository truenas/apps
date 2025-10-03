# walk over ix-dev
import os
import yaml


def ensure_maintainer(data: dict):
    data["maintainers"][0]["email"] = "dev@truenas.com"
    return data


def bump_version(data: dict):
    version = data["version"]
    parts = version.split(".")
    parts[2] = str(int(parts[2]) + 1)
    data["version"] = ".".join(parts)
    data["maintainers"][0]["email"] = "dev@truenas.com"
    return data


def get_yaml_data(file: str):
    with open(file, "r") as f:
        data = yaml.safe_load(f)
        return data


for train in os.listdir("ix-dev"):
    # if its not dir skip
    if not os.path.isdir(os.path.join("ix-dev", train)):
        continue
    for app in os.listdir(os.path.join("ix-dev", train)):
        # if its not dir skip
        if not os.path.isdir(os.path.join("ix-dev", train, app)):
            continue
        file = os.path.join("ix-dev", train, app, "app.yaml")

        data = get_yaml_data(file)
        if not data:
            print("no app.yaml", train, app)
            continue
        if not data["lib_version"] == "2.1.57":
            print("wrong lib_version", train, app, data["lib_version"])
            continue

        data = ensure_maintainer(data)
        # data = bump_version(data)
        # with open(file, "w") as f:
        #     yaml.safe_dump(data, f)
