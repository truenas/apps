#!/usr/bin/env python3
import subprocess
import argparse
import pathlib
import secrets
import shutil
import json
import yaml
import sys
import os

CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"


# Used to print mostly structured data, like yaml or json
# so they can be piped to a file or jq, etc
def print_stdout(msg):
    print(msg)


# Prints to stderr so the output is not mixed with stdout
def print_stderr(msg):
    print(msg, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--app",
        required=True,
        help="The name of the app",
    )
    parser.add_argument(
        "--train",
        required=True,
        help="The name of the train for the app",
    )
    parser.add_argument(
        "--test-file",
        required=True,
        help="Name of the test file to use as values",
    )
    parser.add_argument(
        "--render-only",
        required=False,
        default=False,
        type=bool,
        help="Prints the rendered docker-compose file",
    )
    parser.add_argument(
        "--render-only-debug",
        required=False,
        default=False,
        type=bool,
        help="Prints the rendered docker-compose file even if it's not a valid yaml",
    )
    parsed = parser.parse_args()

    return {
        "app": parsed.app,
        "train": parsed.train,
        "test_file": parsed.test_file,
        "render_only": parsed.render_only,
        "render_only_debug": parsed.render_only_debug,
        "project": secrets.token_hex(16),
    }


def print_info():
    print_stderr("Parameters:")
    print_stderr(f"  - app: [{args['app']}]")
    print_stderr(f"  - train: [{args['train']}]")
    print_stderr(f"  - project: [{args['project']}]")
    print_stderr(f"  - test-file: [{args['test_file']}]")
    print_stderr(f"  - render-only: [{args['render_only']}]")
    print_stderr(f"  - render-only-debug: [{args['render_only_debug']}]")


def command_exists(command):
    return shutil.which(command) is not None


def check_required_commands():
    required_commands = ["docker", "jq", "openssl"]
    for command in required_commands:
        if not command_exists(command):
            print_stderr(f"Error: command [{command}] is not installed")
            sys.exit(1)


def get_base_cmd():
    rendered_compose = "templates/rendered/docker-compose.yaml"
    return " ".join(
        [
            f"docker compose -p {args['project']} -f",
            f"ix-dev/{args['train']}/{args['app']}/{rendered_compose}",
        ]
    )


def pull_app_catalog_container():
    print_stderr(f"Pulling container image [{CONTAINER_IMAGE}]")
    res = subprocess.run(f"docker pull --quiet {CONTAINER_IMAGE}", shell=True, capture_output=True)
    if res.returncode != 0:
        print_stderr(f"Failed to pull container image [{CONTAINER_IMAGE}]")
        sys.exit(1)
    print_stderr(f"Done pulling container image [{CONTAINER_IMAGE}]")


def render_compose():
    print_stderr("Rendering docker-compose file")
    test_values_dir = "templates/test_values"
    app_dir = f"ix-dev/{args['train']}/{args['app']}"
    cmd = " ".join(
        [
            f"docker run --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
            "apps_render_app render",
            f"--path /workspace/{app_dir}",
            f"--values /workspace/{app_dir}/{test_values_dir}/{args['test_file']}",
        ]
    )
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True)
    separator_start()
    if res.returncode != 0:
        print_stderr("Failed to render docker-compose file")
        sys.exit(1)

    with open(f"{app_dir}/templates/rendered/docker-compose.yaml", "r") as f:
        try:
            out = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print_stderr(f"Failed to parse rendered docker-compose file [{e}]")
            with open(f"{app_dir}/templates/rendered/docker-compose.yaml", "r") as f:
                print_stderr(f"Syntax Error in rendered docker-compose file:\n{f.read()}")
            sys.exit(1)

        if args["render_only_debug"]:
            print_stderr("Successfully rendered docker-compose file:")
            print_stdout(yaml.dump(out))
            sys.exit(0)

    print_stderr("Done rendering docker-compose file")


def print_docker_compose_config():
    print_stderr("Printing docker compose config (parsed compose)")
    cmd = f"{get_base_cmd()} config"
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True, capture_output=True)
    separator_end()
    if res.returncode != 0:
        print_stderr("Failed to print docker compose config")
        if res.stdout:
            print_stderr(res.stdout.decode("utf-8"))
        if res.stderr:
            print_stderr(res.stderr.decode("utf-8"))
        sys.exit(1)

    if args["render_only"]:
        print_stdout(res.stdout.decode("utf-8"))
        sys.exit(0)

    print_stderr(res.stdout.decode("utf-8"))


def separator_start():
    print_stderr("=" * 40 + "+++++" + "=" * 40)


def separator_end():
    print_stderr("=" * 40 + "-----" + "=" * 40)


def print_cmd(cmd):
    print_stderr(f"Running command [{cmd}]")


def docker_cleanup():
    cmd = f"{get_base_cmd()} down --remove-orphans --volumes"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()

    cmd = f"{get_base_cmd()} rm --force --stop --volumes"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()


def print_logs():
    cmd = f"{get_base_cmd()} logs"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()


def print_docker_processes():
    cmd = f"{get_base_cmd()} ps --all"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()


def get_failed_containers():
    # Outputs one container per line, in json format
    cmd = f"{get_base_cmd()} ps --all --format json"
    print_cmd(cmd)
    all_containers = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode("utf-8")
    failed_containers = []
    for line in all_containers.split("\n"):
        if not line:
            continue
        try:
            failed_containers.append(json.loads(line))
        except json.JSONDecodeError:
            print_stderr(f"Failed to parse container status output:\n {line}")
            sys.exit(1)

    failed = []
    for container in failed_containers:
        # Skip containers that are exited with 0 (eg init containers),
        # but not restarting (during a restart exit code is 0)
        if all(
            [
                container.get("Health", "") == "" or container.get("Health", "") == "healthy",
                container.get("ExitCode", 0) == 0,
                not container.get("State", "") == "restarting",
            ]
        ):
            print_stderr(
                f"Skipping container [{container['Name']}({container['ID']})] with status [{container.get('State')}]"
                + " because it exited with 0 and has no health status"
            )
            continue
        failed.append(container)

    return failed


def get_container_name(container):
    return container["Name"].replace(args["project"] + "-", "")


def print_inspect_data(container):
    cmd = f"docker container inspect {container['ID']}"
    print_cmd(cmd + f". Container: [{get_container_name(container)}]]")
    res = subprocess.run(cmd, shell=True, capture_output=True)
    data = json.loads(res.stdout.decode("utf-8"))
    separator_start()
    print_stdout(json.dumps(data, indent=4))
    separator_end()


def run_app():
    cmd = f"{get_base_cmd()} up --detach --quiet-pull --wait --wait-timeout 600"
    print_cmd(cmd)
    res = subprocess.run(cmd, shell=True)

    print_docker_processes()
    print_logs()

    print_stderr(f"Exit code: {res.returncode}")
    if res.returncode != 0:
        failed_containers = get_failed_containers()
        print_stderr(f"Found [{len(failed_containers)}] failed containers")
        if failed_containers:
            print_stderr("Failed to start container(s):")
        for container in failed_containers:
            print_stderr(f"Container [{container['Name']}({container['ID']})] exited. Printing Inspect Data")
            print_inspect_data(container)

        # https://github.com/docker/compose/issues/10596
        # `--wait` will return 1 even if a container exits with 0.
        # Although it seems that it only happens on specific compose files, while on others it is not.

        # Cases that a container exits with 0 that are expected is for example an init container.
        return res.returncode if len(failed_containers) > 0 else 0

    print_stderr("Containers started successfully")
    return 0


def check_app_dir_exists():
    if not os.path.exists(f"ix-dev/{args['train']}/{args['app']}"):
        print_stderr(f"App directory [ix-dev/{args['train']}/{args['app']}] does not exist")
        sys.exit(1)


def copy_lib():
    cmd = " ".join(
        [
            f"docker run --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
            "apps_catalog_hash_generate --path /workspace",
        ]
    )
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True, capture_output=True)
    print_stderr(res.stdout.decode("utf-8"))
    separator_start()
    if res.returncode != 0:
        print_stderr("Failed to generate hashes and copy lib")
        sys.exit(1)


def copy_macros():
    if not os.path.exists("macros"):
        print_stderr("Macros directory does not exist. Skipping macros copy")
        return

    print_stderr("Copying macros")
    target_macros_dir = f"ix-dev/{args['train']}/{args['app']}/templates/macros/global"
    os.makedirs(target_macros_dir, exist_ok=True)
    if pathlib.Path(target_macros_dir).exists():
        shutil.rmtree(target_macros_dir, ignore_errors=True)

    try:
        shutil.copytree(
            "macros",
            target_macros_dir,
            dirs_exist_ok=True,
        )
    except shutil.Error:
        print_stderr("Failed to copy macros")
        sys.exit(1)


def generate_item_file():
    with open(f"ix-dev/{args['train']}/{args['app']}/app.yaml", "r") as f:
        app_yaml = yaml.safe_load(f)

    item_file = f"ix-dev/{args['train']}/{args['app']}/item.yaml"
    item_data = {
        "icon_url": app_yaml.get("icon", ""),
        "categories": app_yaml.get("categories", []),
        "screenshots": app_yaml.get("screenshots", []),
        "tags": app_yaml.get("keywords", []),
    }
    with open(item_file, "w") as f:
        yaml.dump(item_data, f)


def main():
    print_info()
    check_app_dir_exists()
    pull_app_catalog_container()
    copy_lib()
    copy_macros()
    generate_item_file()
    check_required_commands()
    render_compose()
    print_docker_compose_config()
    res = run_app()
    docker_cleanup()

    if res == 0:
        print_stderr("Successfully rendered and run docker-compose file")
    else:
        print_stderr("Failed to render and run docker-compose file")

    sys.exit(res)


args = parse_args()

if __name__ == "__main__":
    main()
