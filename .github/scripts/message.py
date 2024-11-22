import os
import sys
import json


def get_files_from_env(env_var: str):
    json_files = os.getenv(env_var, "")
    if not json_files:
        print(f"Environment variable {env_var} is empty", file=sys.stderr)
        exit(1)

    try:
        return json.loads(json_files.replace("\\", ""))
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from {env_var}", file=sys.stderr)
        exit(1)


trains_to_check = ["test", "stable", "enterprise"]
account_to_notify = ["@stavros-k"]


def process(changed_files=[], added_files=[]):
    changes = {}

    for file in changed_files:
        if not file.startswith("ix-dev/"):
            continue
        train = file.split("/")[1]
        if train not in trains_to_check:
            continue

        app = file.split("/")[2]
        if file.startswith(f"ix-dev/{train}/{app}/templates/library/base_"):
            continue

        if train not in changes:
            changes[train] = {"apps": {}}

        if app not in changes[train]["apps"]:
            changes[train]["apps"][app] = {"areas": set([]), "added": set([]), "modified": set([])}

        trimmed_file_name = file.replace(f"ix-dev/{train}/{app}/", "")
        if file in added_files:
            changes[train]["apps"][app]["added"].add(trimmed_file_name)
        else:
            changes[train]["apps"][app]["modified"].add(trimmed_file_name)

        if file.endswith("questions.yaml"):
            changes[train]["apps"][app]["areas"].add("ui")
        elif file.endswith("app.yaml"):
            changes[train]["apps"][app]["areas"].add("metadata")
        elif file.endswith("docker-compose.yaml"):
            changes[train]["apps"][app]["areas"].add("template")
        elif file.endswith("ix_values.yaml"):
            changes[train]["apps"][app]["areas"].add("static_config")

    return generate_message(changes)


def generate_message(changes):
    message = ""
    for train in sorted(changes):
        message += f"## `{train.title()}`\n\n"
        for app in sorted(changes[train]["apps"]):
            message += f"### {app.title()}\n"
            if len(changes[train]["apps"][app]["areas"]) > 0:
                fmt_areas = [f"`{a}`" for a in changes[train]["apps"][app]["areas"]]
                message += f"Affected areas: {', '.join(fmt_areas)}\n"
            if len(changes[train]["apps"][app]["added"]) > 0:
                message += "Added files:\n"
                for file in sorted(changes[train]["apps"][app]["added"]):
                    message += f"- `{file}`\n"
                message += "\n"
            if len(changes[train]["apps"][app]["modified"]) > 0:
                message += "Modified files:\n"
                for file in sorted(changes[train]["apps"][app]["modified"]):
                    message += f"- `{file}`\n"
                message += "\n"
            message += "\n---\n\n"

    if message != "":
        message += "Notifying the following about changes to the trains:\n"
        message += ", ".join(account_to_notify)
    return message


def main():
    changed_files = get_files_from_env("CHANGED_FILES")
    added_files = get_files_from_env("ADDED_FILES")

    print(process(changed_files, added_files))


if __name__ == "__main__":
    main()
