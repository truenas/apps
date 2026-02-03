# walk over ix-dev
import os
import yaml
import subprocess


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


def set_added_date(data: dict, app_yaml: str):
    res = subprocess.run(f'git log --diff-filter=A --format="%as" -- {app_yaml}', shell=True, capture_output=True)
    if res.returncode != 0:
        raise Exception(f"failed to get git log for {app_yaml}")
    git_log = res.stdout.decode("utf-8").strip()
    if data["date_added"] == git_log:
        return data, False
    data["date_added"] = git_log
    return data, True


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
        # if not data["lib_version"] == "2.1.65":
        #     print("wrong lib_version", train, app, data["lib_version"])
        #     continue

        data, changed = set_added_date(data, file)
        if changed:
            data = bump_version(data)
        with open(file, "w") as f:
            yaml.safe_dump(data, f)
