# walk over ix-dev
import os
import yaml

for train in os.listdir("ix-dev"):
    # if its not dir skip
    if not os.path.isdir(os.path.join("ix-dev", train)):
        continue
    for app in os.listdir(os.path.join("ix-dev", train)):
        # if its not dir skip
        if not os.path.isdir(os.path.join("ix-dev", train, app)):
            continue
        qfile = os.path.join("ix-dev", train, app, "questions.yaml")
        with open(qfile, "r") as qf:
            string_data = qf.read()
            if "cifs" not in string_data:
                continue

        file = os.path.join("ix-dev", train, app, "app.yaml")
        with open(file, "r") as f:
            data = yaml.safe_load(f)
            if not data:
                print("no app.yaml", train, app)
                continue
            if not data["lib_version"] == "2.1.53":
                print("wrong lib_version", train, app, data["lib_version"])
                continue

            version = data["version"]
            parts = version.split(".")
            parts[2] = str(int(parts[2]) + 1)
            data["version"] = ".".join(parts)
            data["maintainers"][0]["email"] = "dev@truenas.com"
            with open(file, "w") as f:
                yaml.safe_dump(data, f)
