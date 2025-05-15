import yaml
import os


def main():
    for train in os.listdir("ix-dev"):
        for app in os.listdir(f"ix-dev/{train}"):
            print(train, app)
            app_file = f"ix-dev/{train}/{app}/app.yaml"
            if not os.path.exists(app_file):
                print(f"No values file for {app_file}")
                continue
            with open(app_file, "r") as f:
                data = yaml.safe_load(f.read())
                version = data["version"]
                parts = version.split(".")
                parts[2] = str(int(parts[2]) + 1)
                data["version"] = ".".join(parts)
                with open(app_file, "w") as f:
                    f.write(yaml.dump(data, default_flow_style=False))


if __name__ == "__main__":
    main()
